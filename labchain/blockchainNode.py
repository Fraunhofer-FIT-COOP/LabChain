import json
import logging
import os
from queue import Queue
import sys
import threading
import time
import uuid

from labchain.datastructure.block import Block
from labchain.datastructure.block import LogicalBlock
from labchain.datastructure.blockchain import BlockChain
from labchain.blockchainNodeBootstrap import Bootstrapper
from labchain.util.configReader import ConfigReader
from labchain.util.configReader import ConfigReaderException
from labchain.consensus.consensus import Consensus
from labchain.util.cryptoHelper import CryptoHelper
from labchain.network.networking import JsonRpcClient
from labchain.network.networking import ServerNetworkInterface, NoPeersException
from labchain.datastructure.txpool import TxPool
from labchain.databaseInterface import Db
from labchain import blockchainClient

from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import Transaction, Transaction_Types
import cProfile

class BlockChainNode:

    def __init__(self, config_file_path, node_port=None,
                 peer_list=None):
        """Constructor for BlockChainNode

        Parameters
        ----------
        config_file_path : String
            Path from where to read the Config File
        node_port : Integer
            Port on which Blockchain node will run
        peer_list : List
            List of peers forwarded to the Networking module

        Attributes
        ----------
        consensus_obj : Instance of Consensus module
        crypto_helper_obj : Instance of CryptoHelper module
        blockchain_obj : Instance of BlockChain module
        txpool_obj : Instance of TxPool module
        mine_thread : Thread where mining is run
        orphan_killer : Thread which perodically clean up the orphan blocks
        network_interface : Instance of networking module
        webserver_thread : Thread which runs the webserver
        polling_thread : Thread which polls for additional peers
        network_port : Port for Networking
        initial_peers : Networking module configured with initial neighbour peers
        config_reader : Instance of the ConfigReader module
        db : DB instance for saving the blockchain data to disk
        logger : Instane of logging
        rb_thread : Thread which polls in intervals for blocks requested
        update_worldState: Thread which perodically updates the blockchain's worldState
        """
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
        self.db = None
        self.logger = logging.getLogger(__name__)
        self.rb_thread = None
        self.update_worldState = None
        try:
            self.config_reader = ConfigReader(config_file_path)
            self.logger.debug("Read config file successfully!")
        except ConfigReaderException as e:
            self.logger.error(str(e))
            self.logger.error("Exiting Node startup ..!! \n")
            sys.exit(0)

        self.initialize_components()

    def fetch_prev_blocks(self, q, interval):
        """Fetch the blocks requested at regular intervals, and try to
        add them to the blockchain.

        Parameters
        ----------
        q : Queue
            Queue to store the requested block hashes
        interval : Integer
            The interval to retrieve from Queue and send requests
        """
        while True:
            while not q.empty():
                try:
                    prev_hash = q.get()
                    q.task_done()
                    new_block = self.request_block_by_hash(prev_hash)
                    if new_block:
                        self.blockchain_obj.add_block(new_block)
                except Exception as e:
                    self.logger.error(
                        "Error getting block from neighbour " + str(e))
            time.sleep(interval)

    def schedule_orphans_killing(self, interval):
        """Kill orphan blocks at interval defined"""
        while True:
            self.blockchain_obj.prune_orphans()
            time.sleep(interval)
    
    # def schedule_worldState_update(self, interval):
    #     """Update the worldState at interval definer"""
    #     while True:
    #         if not self.blockchain_obj._worldState_is_updating:
    #             self.blockchain_obj.update_worldState()
    #             time.sleep(interval)

    def block_mine_timer(self, mine_freq, block_transactions_size):
        """Thread which periodically checks to mine
        Note: to start mining based on number of transactions,
        there needs to be either a discussion on few approaches

        Parameters
        ----------
        mine_freq:  Integer
            Periodicity of mining in seconds
        block_transactions_size: Integer
            Maximum number of transactions to put in a block
        """
        next_call = time.time()
        while True:
            # check the last call of mine from consensus component
            if next_call - self.consensus_obj.last_mine_time_sec >= mine_freq:
                transactions = self.txpool_obj.get_transactions(
                    block_transactions_size)
                block = self.blockchain_obj.create_block(transactions)
                self.blockchain_obj.active_mine_block_update(block)
                _timestamp2, _timestamp1, _num_of_blocks, _difficulty = self.blockchain_obj.calculate_diff(
                    block.predecessor_hash)
                self.logger.debug("Created new block, try to mine")
                st = time.time()

                if self.consensus_obj.mine(block, _timestamp2, _timestamp1,
                                           _num_of_blocks, _difficulty):
                    # have to check if other node already created a block
                    self.logger.debug("Mining was successful for new block")
                    if self.blockchain_obj.add_block(block):
                        self.on_new_block_created(block)
                self.logger.debug("Time to mine block is " + str(
                    time.time() - st) + " seconds.")
            self.blockchain_obj.active_mine_block_update(None)
            delay_time = mine_freq - (
                        time.time() - self.consensus_obj.last_mine_time_sec)
            if delay_time < 0:
                delay_time = 1
            self.logger.debug(
                "Mining Thread sleep for {t} secs".format(t=delay_time))
            time.sleep(delay_time)
            next_call = time.time()

    def on_get_transaction(self, transaction_hash):
        """Retrieve a transaction from the blockchain or the transaction
        pool according to the given transaction hash
        """
        transaction_tuple = self.blockchain_obj.get_transaction(
            transaction_hash)
        if not transaction_tuple:
            transaction_tuple = self.txpool_obj.get_transaction_by_hash(
                transaction_hash)
        return transaction_tuple


    def on_get_contract(self, contract_address):
        """Retrieve a contract and it's state from the blockchain according to the given contract hash
        """
        try:
            contract = self.blockchain_obj.worldState.get_contract(contract_address)
            return contract.to_dict()
        except:
            return None


    def on_get_contract_state(self, contract_address):
        """Retrieve a contract and it's state from the blockchain according to the given contract hash
        """
        state = self.blockchain_obj.worldState.get_state(contract_address)
        return state
    
    def on_get_methods(self, state, contract_address):
        """Get the methods of a contract
        """
        methods = self.blockchain_obj.worldState.get_methods(contract_address)
        return methods

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
            self.logger.warning('Block #' + str(
                block.block_id) + ' could not be sent to any peer')

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
        """Request a block from other peers according to a block hash"""
        try:
            return self.network_interface.requestBlockByHash(hash)
        except Exception:
            return None

    def request_block_by_id(self, block_id):
        """Request a block from other peers according to a block id"""
        return self.network_interface.requestBlock(block_id)

    def create_network_interface(self, port, initial_peers=None):
        """Initialize the network interface"""
        if initial_peers is None:
            initial_peers = {}
        return ServerNetworkInterface(JsonRpcClient(), initial_peers,
                                      self.crypto_helper_obj,
                                      self.on_new_block_received,
                                      self.on_new_transaction_received,
                                      self.on_get_block_by_id,
                                      self.on_get_block_by_hash,
                                      self.on_get_transaction,
                                      self.on_get_contract,
                                      self.on_get_contract_state,
                                      self.on_get_methods,
                                      self.on_get_blocks_by_range,
                                      port)

    def reinitialize_blockchain_from_db(self):
        """Restore DB by fetching entries from Blockchain"""
        return self.db.get_blockchain_from_db()

    def initialize_components(self):
        """ Initialize every componenent of the node"""
        self.logger.debug("Initialized every component for the node")
        self.consensus_obj = Consensus()
        self.crypto_helper_obj = CryptoHelper.instance()
        self.txpool_obj = TxPool(crypto_helper_obj=self.crypto_helper_obj)
        self.db = Db(block_chain_db_file=os.path.abspath(os.path.join(
                     os.path.dirname(__file__), 'resources/labchaindb.sqlite')))

        """init blockchain"""
        # Generate the node ID using host ID
        node_uuid = str(uuid.uuid1())
        node_id = node_uuid[node_uuid.rfind('-') + 1:]
        self.logger.info("Creator id " + str(node_id))

        # Read all configurations to be used
        try:
            tolerance_value = self.config_reader.get_config(
                section='BLOCK_CHAIN',
                option='TOLERANCE_LEVEL')
            pruning_interval = self.config_reader.get_config(
                section='BLOCK_CHAIN',
                option='TIME_TO_PRUNE')
            fetch_prev_interval = self.config_reader.get_config(
                                  section='BLOCK_CHAIN',
                                  option='FETCH_PREV_INTERVAL')
            if not self.network_port:
                self.network_port = self.config_reader.get_config(
                    section='NETWORK',
                    option='PORT')
            initial_peers_from_config = self.config_reader.get_config(
                section='NETWORK',
                option='PEER_LIST')
            pool_interval = self.config_reader.get_config(section='NETWORK',
                                                          option='POOLING_INTERVAL_SEC')
            mine_freq = self.config_reader.get_config(section='MINING',
                                                      option='MINE_SCHEDULING_FREQUENCY_SEC')
            num_of_transactions = self.config_reader.get_config(
                section='MINING',
                option='BLOCK_TRANSACTION_SIZE')
            min_blocks = self.config_reader.get_config(section='MINING',
                                                       option='NUM_OF_BLOCKS_FOR_DIFFICULTY')
        except ConfigReaderException as e:
            self.logger.error(str(e))
            self.logger.error("Exiting Node startup ..!! \n")
            sys.exit(0)

        # Create tables if not already
        self.db.create_tables()

        self.q = Queue()

        self.blockchain_obj = BlockChain(node_id=node_id,
                                         tolerance_value=tolerance_value,
                                         pruning_interval=pruning_interval,
                                         consensus_obj=self.consensus_obj,
                                         txpool_obj=self.txpool_obj,
                                         crypto_helper_obj=self.crypto_helper_obj,
                                         min_blocks_for_difficulty=min_blocks,
                                         db=self.db,
                                         q=self.q)
        
        
        
        #self.create_dummy_method_calls(1000)
        #self.create_dummy_contract(500)


        self.logger.debug("Initialized web server")
        """init network interface"""
        intial_peer_list = self.initial_peers
        if not intial_peer_list:
            intial_peer_list = json.loads(initial_peers_from_config)
            self.initial_peers = initial_peers_from_config
        self.network_interface = self.create_network_interface(
            self.network_port,
            initial_peers=intial_peer_list)

        # start the web servers for receiving JSON-RPC calls
        self.logger.debug('Starting web server thread...')
        self.webserver_thread = threading.Thread(name='Web Server',
                                                 target=self.network_interface.start_listening)
        self.webserver_thread.start()

        # start the polling threads
        self.logger.debug('Starting polling threads...')
        self.polling_thread = threading.Thread(name='Polling',
                                               target=self.network_interface.poll_update_peer_lists,
                                               args=(pool_interval,))
        self.polling_thread.start()

        self.logger.info("Fetching Blocks from Database if present...")
        blocks_from_db = self.reinitialize_blockchain_from_db()
        if blocks_from_db is not None:
            for block in blocks_from_db:
                self.blockchain_obj.add_block(
                    LogicalBlock.from_block(block, self.consensus_obj), False)
                self.logger.info(
                    'Fetched block nr ' + str(block.block_id) + ' from DB')

        self.logger.info("Starting bootstrap...")
        """Bootstrap the blockchain node"""
        bootstrapper = Bootstrapper(self.network_interface)
        bootstrapper.do_bootstrap(self.blockchain_obj)

        self.logger.debug("Starting request block thread...")
        """init rb"""
        # start the scheduler for rb
        self.rb_thread = threading.Thread(target=self.fetch_prev_blocks,
                                          kwargs=dict(q=self.q,
                                                      interval=fetch_prev_interval))
        self.rb_thread.start()

        self.logger.debug("Starting mining thread...")
        """init mining"""
        # start the scheduler for mining
        self.mine_thread = threading.Thread(target=self.block_mine_timer,
                                            kwargs=dict(mine_freq=mine_freq,
                                                        block_transactions_size=num_of_transactions))
        
        
        
        
        
        self.logger.debug("Starting orphan pruning thread...")
        self.orphan_killer = threading.Thread(
            target=self.schedule_orphans_killing,
            kwargs=dict(interval=pruning_interval))
        self.logger.debug("Starting worldState thread...")


        #self.block_mine_timer(mine_freq,num_of_transactions)
        self.mine_thread.start()
        self.orphan_killer.start()

    


    def create_dummy_method_calls(self, number_of_calls):

        contract_address = self.create_dummy_contract()
        print("Transaction for creating a test contract sent...")

        #time.sleep(15)

        chosen_receiver = contract_address
        
        crypto_helper = CryptoHelper.instance()
        private_key, public_key = crypto_helper.generate_key_pair()

        payload = {'methods':[]}
        methods = []

        methodName = 'addCoins'
        arguments = json.loads("""{"coinsToAdd": 100}""")
        
        arguments = json.dumps(arguments)
        arguments = arguments.replace('{','{"sender": "' + public_key + '", ', 1)
        arguments = json.loads(arguments)

        methodToCall = {'methodName':methodName, 'arguments':arguments}
        methods.append(methodToCall)

        payload['methods'] = methods

        payload['contract_file_name'] = 'contract.py'

        for i in range(19):
            new_transaction = Transaction(sender=str(public_key), receiver=chosen_receiver, payload='', transaction_type='Normal Transaction')
            transaction_hash = crypto_helper.hash(new_transaction.get_json())
            new_transaction.transaction_hash = transaction_hash
            new_transaction.sign_transaction(crypto_helper, private_key)
            self.txpool_obj.add_transaction_if_not_exist(new_transaction)
            print('Normal transaction # ' + str(i) + ' was sent.')

        for i in range(number_of_calls):
            new_transaction = Transaction(sender=str(public_key), receiver=chosen_receiver, payload=str(payload), transaction_type='Method Call')
            transaction_hash = crypto_helper.hash(new_transaction.get_json())
            new_transaction.transaction_hash = transaction_hash
            new_transaction.sign_transaction(crypto_helper, private_key)
            self.txpool_obj.add_transaction_if_not_exist(new_transaction)
            print('Method call transaction # ' + str(i) + ' was sent.')

        

    def create_dummy_contract(self, num_of_contracts):
        for _ in range(num_of_contracts):
            crypto_helper = CryptoHelper.instance()
            payload = {"contractCode":'', "arguments":"", "contract_file_name":""}

            payload["contractCode"] = """gANCGQwAAIADWA8MAAAiIiIKICAgIENPTlRSQUNUIEdVSURFTElORVMKICAgIC0gQ29udHJhY3Qg\naGFzIHRvIGhhdmUgYSAidG9fZGljdCIgbWV0aG9kLgogICAgLSBUaGUgY29uc3RydWN0b3IgbmVl\nZHMgdG8gcmVjZWl2ZSB0aGUgc2VuZGVyIG9mIHRoZSB0cmFuc2FjdGlvbgogICAgICAgIGFzIGEg\ncGFyYW1ldGVyIGFuZCBzYXZlIGl0IGluIHNlbGYuY29udHJhY3Rfb3duZXJzIGFzIHRoZSBmaXJz\ndAogICAgICAgIHN0cmluZyBvZiBhIGxpc3QuCiAgICAgICAgTm90ZTogVGhlIHNlbmRlciBpcyBp\nbmplY3RlZCBieSB0aGUgYmxvY2tjaGFpbl9ub2RlIGxvZ2ljIGludG8gdGhlCiAgICAgICAgICAg\nIHBhcmFtZXRlcnMgb2YgdGhlIGNvbnRyYWN0IGNhbGwsIHNvIGl0IHNob3VsZCBiZSBvbW1pdGVk\nIHdoZW4gY3JlYXRpbmcKICAgICAgICAgICAgYSBjb250cmFjdCBjcmVhdGlvbiB0cmFuc2FjdGlv\nbiBvciBhIG1ldGhvZCBjYWxsIHRyYW5zYWN0aW9uIGluIHRoZQogICAgICAgICAgICBibG9ja2No\nYWluIGNsaWVudC4KICAgIC0gVGhlIGJhZF9zdGF0ZSB2YXJpYWJsZSBzaG91bGQgYmUgdXNlZCBp\nbnNpZGUgb2YgdGhlIGNvbnRyYWN0cyBsb2dpYyB0byBpbmZvcm0KICAgICAgICB0aGF0IGEgdHJh\nbnNhY3Rpb24gY3JlYXRlZCBhbiB1bmRlc2lyZWQgc3RhdGUuIEl0J3MgZGVmYXVsdCBpcyBGYWxz\nZS4gSWYgc2V0IHRvCiAgICAgICAgVHJ1ZSB0aGUgYmxvY2tjaGFpbiB3aWxsIGRpc2NhcmQgdGhl\nIHRyYW5zYWN0aW9uIHRoYXQgY3JlYXRlZCB0aGlzIGNoYW5nZSBhbmQKICAgICAgICB0aGUgbmV3\nIHN0YXRlIHdpbGwgbm90IGJlIHNhdmVkLgogICAgLSBBbGwgcGFyYW1ldGVyIHR5cGVzIHNob3Vs\nZCBiZSBzcGVjaWZpZWQgaW4gdGhlIGNvbnN0cnVjdG9yIGFuZCBpbiB0aGUgY2xhc3MgbWV0aG9k\ncy4KICAgIC0gQWxsIGN1c3RvbSBtZXRob2RzIHNob3VsZCByZWNlaXZlIHRoZSBzZW5kZXIgYXMg\ndGhlIGZpcnN0IHBhcmFtZXRlci4gVGhlIG1ldGhvZCBjYW4gdGhlbgogICAgCXVzZSB0aGlzIGlu\nZm9ybWF0aW9uIHRvIHJlc3RyaWN0IGFjdGlvbnMgb3Igbm90LgoKICAgIC0gRXhhbXBsZToKICAg\nICAgICBjbGFzcyBteUNvbnRyYWN0OgogICAgICAgICAgICBkZWYgX19pbml0X18oc2VsZiwgc2Vu\nZGVyOiBzdHIsIGN1c3RvbV9wYXJhbTE6IHR5cGUsIGN1c3RvbV9wYXJhbTI6IHR5cGUsIC4uLik6\nCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICNSRVFVSVJFRCBBVFRSSUJVVEVTCiAg\nICAgICAgICAgICAgICBzZWxmLmNvbnRyYWN0X25hbWUgPSBzZWxmLl9fY2xhc3NfXy5fX25hbWVf\nXwogICAgICAgICAgICAgICAgc2VsZi5iYWRfc3RhdGUgPSBGYWxzZQogICAgICAgICAgICAgICAg\nc2VsZi5jb250cmFjdF9vd25lcnMgPSBbc2VuZGVyXQoKICAgICAgICAgICAgICAgICNDVVNUT00g\nQVRUUklCVVRFUwogICAgICAgICAgICAgICAgc2VsZi5jdXN0b21fYXJnMSA9IGN1c3RvbV9hcmcx\nCiAgICAgICAgICAgICAgICBzZWxmLmN1c3RvbV9hcmcyID0gY3VzdG9tX2FyZzIKICAgICAgICAg\nICAgICAgIC4uLgoKICAgICAgICAgICAgI1JFUVVJUkVEIE1FVEhPRAogICAgICAgICAgICBkZWYg\ndG9fZGljdChzZWxmKToKICAgICAgICAgICAgICAgIHJldHVybiB7CiAgICAgICAgICAgICAgICAg\nICAgI1JFUVVJUkVEIEtFWSBWQUxVRSBQQUlSUwogICAgICAgICAgICAgICAgICAgICdjb250cmFj\ndF9uYW1lJzogc2VsZi5jb250cmFjdF9uYW1lLAogICAgICAgICAgICAgICAgICAgICdiYWRfc3Rh\ndGUnOiBzZWxmLmJhZF9zdGF0ZSwKICAgICAgICAgICAgICAgICAgICAnY29udHJhY3Rfb3duZXJz\nJzogc2VsZi5jb250cmFjdF9vd25lcnMsCiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAg\nICAgICAgICAgI0NVU1RPTSBLRVkgVkFMVUUgUEFJUlMKICAgICAgICAgICAgICAgICAgICAnY3Vz\ndG9tX2FyZzEnID0gc2VsZi5jdXN0b21fYXJnMSwKICAgICAgICAgICAgICAgICAgICAnY3VzdG9t\nX2FyZzInID0gc2VsZi5jdXN0b21fYXJnMiwKICAgICAgICAgICAgICAgICAgICAuLi4KICAgICAg\nICAgICAgICAgICAgICB9CgogICAgICAgICAgICAjQ1VTVE9NIE1FVEhPRFMKICAgICAgICAgICAg\nZGVmIG15X2N1c3RvbV9tZXRob2Qoc2VsZiwgc2VuZGVyOiBzdHIsIG15X2N1c3RvbV9wYXJhbTE6\nIHR5cGUsIC4uLikKICAgICAgICAgICAgLi4uCiIiIgoKY2xhc3MgQ29udHJhY3Q6CiAgICBkZWYg\nX19pbml0X18oc2VsZiwgc2VuZGVyOiBzdHIsIHBlcnNvbjogc3RyLCBjb2luczogaW50KToKICAg\nICAgICBzZWxmLmNvbnRyYWN0X25hbWUgPSBzZWxmLl9fY2xhc3NfXy5fX25hbWVfXwogICAgICAg\nIHNlbGYuYmFkX3N0YXRlID0gRmFsc2UKICAgICAgICBzZWxmLmNvbnRyYWN0X293bmVycyA9IFtz\nZW5kZXJdCgogICAgICAgIHNlbGYucGVyc29uOiBzdHIgPSBwZXJzb24KICAgICAgICBzZWxmLmNv\naW5zOiBpbnQgPSBjb2lucwoKCiAgICBkZWYgdG9fZGljdChzZWxmKToKICAgICAgICAiIiJDb252\nZXJ0IG93biBkYXRhIHRvIGEgZGljdGlvbmFyeS4iIiIKICAgICAgICByZXR1cm4gewogICAgICAg\nICAgICAnY29udHJhY3RfbmFtZSc6IHNlbGYuY29udHJhY3RfbmFtZSwKICAgICAgICAgICAgJ2Nv\nbnRyYWN0X293bmVycyc6IHNlbGYuY29udHJhY3Rfb3duZXJzLAogICAgICAgICAgICAnYmFkX3N0\nYXRlJzogc2VsZi5iYWRfc3RhdGUsCiAgICAgICAgICAgICdwZXJzb24nOiBzZWxmLnBlcnNvbiwK\nICAgICAgICAgICAgJ2NvaW5zJzogc2VsZi5jb2lucwogICAgICAgICAgICB9CgoKICAgIGRlZiBh\nZGRDb2lucyhzZWxmLCBzZW5kZXI6IHN0ciwgY29pbnNUb0FkZDogaW50KToKICAgICAgICBzZWxm\nLmNvaW5zID0gc2VsZi5jb2lucyArIGNvaW5zVG9BZGQKCiAgICBkZWYgc3BlbmRDb2lucyhzZWxm\nLCBzZW5kZXI6IHN0ciwgY29pbnNUb1NwZW5kOiBpbnQpOgogICAgICAgIGlmIHNlbGYuY29pbnMg\nLSBjb2luc1RvU3BlbmQgPCAwOgogICAgICAgICAgICBzZWxmLmJhZF9zdGF0ZSA9IFRydWUKICAg\nICAgICAgICAgcmV0dXJuCiAgICAgICAgZWxzZToKICAgICAgICAgICAgc2VsZi5jb2lucyA9IHNl\nbGYuY29pbnMgLSBjb2luc1RvU3BlbmRxAC5xAC4=\n"""
            payload['arguments'] = json.loads('{"Person": "Alice", "coins": 100}')
            payload['contract_file_name'] = 'contract.py'

            private_key, public_key = crypto_helper.generate_key_pair()
            new_transaction = Transaction(sender=str(public_key), receiver='', payload=str(payload), transaction_type='Contract Creation')
            transaction_hash = crypto_helper.hash(new_transaction.get_json())
            new_transaction.transaction_hash = transaction_hash
            new_transaction.sign_transaction(crypto_helper, private_key)
            self.txpool_obj.add_transaction_if_not_exist(new_transaction)
            print("Contract added")

            #return transaction_hash
