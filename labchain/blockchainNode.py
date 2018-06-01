import configparser
import json
import logging
import sys
import threading
import time
import uuid

from labchain.block import LogicalBlock
from labchain.bootstrap import Bootstrapper
from labchain.consensus import Consensus
from labchain.cryptoHelper import CryptoHelper
from labchain.txpool import TxPool
from labchain.blockchain import BlockChain
from labchain.networking import ServerNetworkInterface, JsonRpcClient

NODE_CONFIG_FILE = 'resources/node_configuration.ini'
# change to DEBUG to see more output
LOG_LEVEL = logging.INFO


class BlockChainNode:

    def __init__(self):
        self.consensus_obj = None
        self.crypto_helper_obj = None
        self.blockchain_obj = None
        self.txpool_obj = None
        self.mine_thread = None
        self.orphan_killer = None
        self.network_interface = None
        self.webserver_thread = None
        self.polling_thread = None
        self.initialize_components()

        self.config = None
        try:
            self.config = configparser.ConfigParser()
            self.config.read(NODE_CONFIG_FILE)
        except Exception:
            logging.error('Node Configuration file is corrupt or non-existent, exiting node startup.... \n')
            sys.exit(0)

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
            if self.consensus_obj.last_mine_time_sec >= mine_freq:
                transactions = self.txpool_obj.get_transactions(block_transactions_size)
                block = self.blockchain_obj.create_block(transactions)
                _timestamp2, _timestamp1, _num_of_blocks = self.blockchain_obj.calculate_diff()
                self.consensus_obj.mine(block, _timestamp2, _timestamp1, _num_of_blocks)
                # have to check if other node already created a block
                if self.blockchain_obj.add_block(block):
                    self.on_new_block_created(block.get_json())

            next_call += (mine_freq - self.consensus_obj.last_mine_time_sec)
            time.sleep(next_call - time.time())

    # TODO: abort mining 1) when equal block or 2)

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
        lblock = LogicalBlock.from_block(block)
        return self.blockchain_obj.add_block(lblock)

    def on_new_block_created(self, lblock):
        """When a new block is mined, send the block to other nodes via network"""
        block = lblock.get_block_obj()
        self.network_interface.sendBlock(block)
        pass

    def on_get_block_by_hash(self, hash):
        """callback method for get block"""
        return self.blockchain_obj.get_block_by_hash(hash)

    def on_get_block_by_id(self):
        """callback method for get block"""
        pass

    def create_network_interface(self, port, initial_peers=None):
        if initial_peers is None:
            initial_peers = {}
        return ServerNetworkInterface(JsonRpcClient(), initial_peers, self.crypto_helper_obj,
                                      self.on_new_block_received,
                                      self.on_new_transaction_received,
                                      self.on_get_block_by_id, self.on_get_transaction, port)

    def get_config_int(self, section, option, fallback=None):
        try:
            value = self.config.getint(section=section,
                                       option=option,
                                       fallback=fallback)
            return value
        except Exception:
            logging.error("Error reading from config")

    def get_config_string(self, section, option, fallback=None):
        try:
            value = self.config.get(section=section,
                                    option=option,
                                    fallback=fallback)
            return value
        except Exception:
            logging.error("Error reading from config")

    def initialize_components(self):
        """ Initialize every componenent of the node"""

        self.consensus_obj = Consensus()
        self.crypto_helper_obj = CryptoHelper.instance()
        self.txpool_obj = TxPool(crypto_helper_obj=self.crypto_helper_obj)

        """init blockchain"""
        # Generate the node ID using host ID
        node_uuid = str(uuid.uuid1())
        node_id = node_uuid[node_uuid.rfind('-') + 1:]

        tolerance_value = self.get_config_int(section='BLOCK_CHAIN',
                                              option='TOLERANCE_LEVEL')
        pruning_interval = self.get_config_int(section='BLOCK_CHAIN',
                                               option='TIME_TO_PRUNE')
        self.blockchain_obj = BlockChain(node_id=node_id, tolerance_value=tolerance_value,
                                         pruning_interval=pruning_interval, consensus_obj=self.consensus_obj,
                                         txpool_obj=self.txpool_obj, crypto_helper_obj=self.crypto_helper_obj)

        """init network interface"""
        intial_peer_list = json.loads(self.get_config_string(section='NETWORK',
                                                             option='PEER_LIST'))
        network_port = self.get_config_int(section='NETWORK',
                                           option='PORT')
        self.network_interface = self.create_network_interface(network_port, initial_peers=intial_peer_list)

        # start the web servers for receiving JSON-RPC calls
        logging.debug('Starting web server thread...')
        self.webserver_thread = threading.Thread(name='Web Server',
                                                 target=self.network_interface.start_listening,
                                                 args=(False,))
        self.webserver_thread.start()
        logging.debug('Done')

        # start the polling threads
        logging.debug('Starting polling threads...')
        pool_interval = self.get_config_int(section='NETWORK',
                                            option='POOLING_INTERVAL_SEC')
        self.polling_thread = threading.Thread(name='Polling',
                                               target=self.network_interface.poll_update_peer_lists,
                                               args=(pool_interval,))
        self.polling_thread.start()
        logging.debug('Done')

        """Bootstrap the blockchain node"""
        bootstrapper = Bootstrapper(self.network_interface)
        bootstrapper.do_bootstrap(self.blockchain_obj)

        """init mining"""
        # start the scheduler for mining
        mine_freq = self.get_config_int(section='MINING',
                                        option='MINE_SCHEDULING_FREQUENCY_SEC')
        num_of_transactions = self.get_config_int(section='MINING',
                                                  option='BLOCK_TRANSACTION_SIZE')

        self.mine_thread = threading.Thread(target=self.block_mine_timer,
                                            kwargs=dict(mine_freq=mine_freq,
                                                        num_of_transactions=num_of_transactions))
        self.mine_thread.start()

        self.orphan_killer = threading.Thread(target=self.schedule_orphans_killing,
                                              kwargs=dict(interval=pruning_interval))

        self.orphan_killer.start()


def configure_logging():
    logging.basicConfig(level=logging.WARNING, format='%(threadName)s: %(message)s')
    logging.getLogger(BlockChainNode.__name__).setLevel(LOG_LEVEL)


if __name__ == '__main__':
    configure_logging()
    blockchain_node = BlockChainNode()
