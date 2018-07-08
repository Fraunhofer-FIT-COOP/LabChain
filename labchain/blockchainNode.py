import json
import logging
import sys
import threading
import time
import uuid
import os

from labchain.block import Block
from labchain.block import LogicalBlock
from labchain.blockchain import BlockChain
from labchain.bootstrap import Bootstrapper
from labchain.configReader import ConfigReader
from labchain.configReader import ConfigReaderException
from labchain.consensus import Consensus
from labchain.cryptoHelper import CryptoHelper
from labchain.networking import JsonRpcClient
from labchain.networking import ServerNetworkInterface, NoPeersException
from labchain.txpool import TxPool
from labchain.dashboardDB import DashBoardDB
from labchain.db import Db

logger = logging.getLogger(__name__)


class BlockChainNode:

    def __init__(self, config_file_path, event_bus, node_port=None, peer_list=None):
        self.event_bus = event_bus
        self.consensus_obj = None
        self.crypto_helper_obj = None
        self.blockchain_obj = None
        self.txpool_obj = None
        self.mine_thread = None
        self.orphan_killer = None
        self.network_interface = None
        self.webserver_thread = None
        self.polling_thread = None
        self.network_port = node_port
        self.initial_peers = peer_list
        self.config_reader = None
        self.dash_board_db = None
        self.db = None
        try:
            self.config_reader = ConfigReader(config_file_path)
            logger.debug("Read config file successfully!")
        except ConfigReaderException as e:
            logger.error(str(e))
            logger.error("Exiting Node startup ..!! \n")
            sys.exit(0)

        self.initialize_components()

    def schedule_orphans_killing(self, interval):
        while True:
            self.blockchain_obj.prune_orphans()
            time.sleep(interval)

    def block_mine_timer(self, mine_freq, block_transactions_size):
        """ Thread which periodically checks to mine
        Note: to start mining based on number of transactions,
        there needs to be either a discussion on few approaches

            Args:
                mine_freq (integer): periodicity of mining in seconds
                block_transactions_size (integer): max transactions in a block
        """
        next_call = time.time()
        while True:
            # check the last call of mine from consensus component
            if next_call - self.consensus_obj.last_mine_time_sec >= mine_freq:
                transactions = self.txpool_obj.get_transactions(block_transactions_size)
                block = self.blockchain_obj.create_block(transactions)
                self.blockchain_obj.active_mine_block_update(block)
                _timestamp2, _timestamp1, _num_of_blocks, _difficulty = self.blockchain_obj.calculate_diff()
                logger.debug("Created new block, try to mine")
                st = time.time()
                if self.dash_board_db.get_mining_status() == 1:
                    if self.consensus_obj.mine(block, _timestamp2, _timestamp1, _num_of_blocks, _difficulty):
                     # have to check if other node already created a block
                        logger.debug("Mining was successful for new block")
                        if self.blockchain_obj.add_block(block):
                            self.on_new_block_created(block)
                    logger.debug("Time to mine block is " + str(time.time() - st) + " seconds.")
            self.blockchain_obj.active_mine_block_update(None)
            delay_time = mine_freq - (time.time() - self.consensus_obj.last_mine_time_sec)
            if delay_time < 0:
                delay_time = 1
            logger.debug("Mining Thread sleep for {t} secs".format(t=delay_time))
            time.sleep(delay_time)
            next_call = time.time()

    def on_get_transaction(self, transaction_hash):
        transaction_tuple = self.blockchain_obj.get_transaction(transaction_hash)
        if not transaction_tuple:
            transaction_tuple = self.txpool_obj.get_transaction_by_hash(transaction_hash)
        return transaction_tuple

    def on_new_transaction_received(self, transaction):
        """Callback method to pass to network"""
        return self.txpool_obj.add_transaction_if_not_exist(transaction)

    def on_new_block_received(self, block):
        """Callback method to pass to network, call add block method in block chain"""
        return self.blockchain_obj.add_block(block)

    def on_new_block_created(self, lblock):
        """When a new block is mined, send the block to other nodes via network"""
        block = lblock.get_block_obj()
        try:
            self.network_interface.sendBlock(block)
        except NoPeersException:
            logger.warning('Block #' + str(block.block_id) + ' could not be sent to any peer')

    def on_get_block_by_hash(self, hash):
        """callback method for get block"""
        block_data = self.blockchain_obj.get_block_by_hash(hash)
        if block_data:
            return Block.from_json(block_data)
        return None

    def on_get_block_by_id(self, block_id):
        """callback method for get block"""
        return self.blockchain_obj.get_block_by_id(block_id)

    def on_get_blocks_by_range(self, range_start=None, range_end=None):
        """callback method for get blocks by range"""
        return self.blockchain_obj.get_block_range(range_start, range_end)

    def request_block_by_hash(self, hash):
        try:
            return self.network_interface.requestBlockByHash(hash)
        except Exception:
            return None

    def request_block_by_id(self, block_id):
        return self.network_interface.requestBlock(block_id)

    def create_network_interface(self, port, initial_peers=None):
        if initial_peers is None:
            initial_peers = {}
        return ServerNetworkInterface(JsonRpcClient(), initial_peers, self.crypto_helper_obj,
                                      self.on_new_block_received,
                                      self.on_new_transaction_received,
                                      self.on_get_block_by_id,
                                      self.on_get_block_by_hash,
                                      self.on_get_transaction,
                                      self.on_get_blocks_by_range,
                                      port)

    def reinitialize_blockchain_from_db(self):
        return self.db.get_blockchain_from_db()

    def initialize_components(self):
        """ Initialize every componenent of the node"""
        logger.debug("Initialized every component for the node")
        self.consensus_obj = Consensus()
        self.crypto_helper_obj = CryptoHelper.instance()
        self.dash_board_db = DashBoardDB.instance()
        self.txpool_obj = TxPool(crypto_helper_obj=self.crypto_helper_obj)
        self.db = Db(block_chain_db_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      'resources/labchaindb.sqlite')))

        """init blockchain"""
        # Generate the node ID using host ID
        node_uuid = str(uuid.uuid1())
        node_id = node_uuid[node_uuid.rfind('-') + 1:]
        #node_id = node_uuid
        logger.info("Creator id " + str(node_id))

        # Read all configurations to be used
        try:
            tolerance_value = self.config_reader.get_config(section='BLOCK_CHAIN',
                                                            option='TOLERANCE_LEVEL')
            pruning_interval = self.config_reader.get_config(section='BLOCK_CHAIN',
                                                             option='TIME_TO_PRUNE')
            if not self.network_port:
                self.network_port = self.config_reader.get_config(section='NETWORK',
                                                                  option='PORT')
            initial_peers_from_config = self.config_reader.get_config(section='NETWORK',
                                                                      option='PEER_LIST')
            pool_interval = self.config_reader.get_config(section='NETWORK',
                                                          option='POOLING_INTERVAL_SEC')
            mine_freq = self.config_reader.get_config(section='MINING',
                                                      option='MINE_SCHEDULING_FREQUENCY_SEC')
            num_of_transactions = self.config_reader.get_config(section='MINING',
                                                                option='BLOCK_TRANSACTION_SIZE')
            min_blocks = self.config_reader.get_config(section='MINING',
                                                       option='NUM_OF_BLOCKS_FOR_DIFFICULTY')
        except ConfigReaderException as e:
            logger.error(str(e))
            logger.error("Exiting Node startup ..!! \n")
            sys.exit(0)

        # Create tables if not already
        self.db.create_tables()

        self.blockchain_obj = BlockChain(node_id=node_id, tolerance_value=tolerance_value,
                                         pruning_interval=pruning_interval,
                                         consensus_obj=self.consensus_obj,
                                         txpool_obj=self.txpool_obj,
                                         crypto_helper_obj=self.crypto_helper_obj,
                                         min_blocks_for_difficulty=min_blocks,
                                         request_block_callback=self.request_block_by_id,
                                         request_block_hash_callback=self.request_block_by_hash,
                                         event_bus=self.event_bus, db=self.db)

        logger.debug("Initialized web server")
        """init network interface"""
        intial_peer_list = self.initial_peers
        if not intial_peer_list:
            intial_peer_list = json.loads(initial_peers_from_config)
            self.initial_peers = initial_peers_from_config
        self.network_interface = self.create_network_interface(self.network_port,
                                                               initial_peers=intial_peer_list)

        # start the web servers for receiving JSON-RPC calls
        logger.debug('Starting web server thread...')
        self.webserver_thread = threading.Thread(name='Web Server',
                                                 target=self.network_interface.start_listening)
        self.webserver_thread.start()

        # start the polling threads
        logger.debug('Starting polling threads...')
        self.polling_thread = threading.Thread(name='Polling',
                                               target=self.network_interface.poll_update_peer_lists,
                                               args=(pool_interval,))
        self.polling_thread.start()

        logger.info("Starting bootstrap...")
        """Bootstrap the blockchain node"""
        bootstrapper = Bootstrapper(self.network_interface)
        blocks_from_db = self.reinitialize_blockchain_from_db()
        if blocks_from_db is not None:
            for block in blocks_from_db:
                self.blockchain_obj.add_block(LogicalBlock.from_block(block, self.consensus_obj), False)
                logger.info('Fetched block ' + str(block.block_id) + ' from DB')
        bootstrapper.do_bootstrap(self.blockchain_obj)

        logger.debug("Starting mining thread...")
        """init mining"""
        # start the scheduler for mining
        self.mine_thread = threading.Thread(target=self.block_mine_timer,
                                            kwargs=dict(mine_freq=mine_freq,
                                                        block_transactions_size=num_of_transactions))
        self.mine_thread.start()

        logger.debug("Starting orphan pruning thread...")
        self.orphan_killer = threading.Thread(target=self.schedule_orphans_killing,
                                              kwargs=dict(interval=pruning_interval))

        self.orphan_killer.start()
