import unittest
import os

from labchain.datastructure.blockchain import BlockChain
from labchain.consensus.consensus import Consensus
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import Transaction
from labchain.datastructure.taskTransaction import WorkflowTransaction
from labchain.datastructure.txpool import TxPool
from labchain.util.configReader import ConfigReader
from labchain.databaseInterface import Db

test_resources_dic_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './resources'))
test_db_file = test_resources_dic_path + '/labchaindb.sqlite'
test_node_config_file = test_resources_dic_path + '/node_configuration.ini'


class DbTestCase(unittest.TestCase):

    def setUp(self):
        self.database = Db(test_db_file)
        self.init_components()

    def init_components(self):
        config_reader = ConfigReader(test_node_config_file)

        tolerance = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TOLERANCE_LEVEL')
        pruning = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TIME_TO_PRUNE')
        min_blocks = config_reader.get_config(
            section='MINING',
            option='NUM_OF_BLOCKS_FOR_DIFFICULTY')

        self.consensus = Consensus()
        self.crypto_helper_obj = CryptoHelper.instance()
        self.txpool = TxPool(self.crypto_helper_obj)
        self.block_list = []
        self.blockchain = BlockChain(node_id="nodeId1", tolerance_value=tolerance,
                                     pruning_interval=pruning,
                                     consensus_obj=self.consensus,
                                     txpool_obj=self.txpool,
                                     crypto_helper_obj=self.crypto_helper_obj,
                                     min_blocks_for_difficulty=min_blocks,
                                     db=self.database,
                                     q=None)

    def test_create_tables(self):
        self.database.open_connection(test_db_file)
        self.assertTrue(self.database.create_tables())

    def test_save_block(self):
        block = self.get_block()
        self.assertTrue(self.database.save_block(block))
        self.assertEqual(self.database.get_blockchain_from_db()[0], block)

    def test_workflow_transaction(self):
        workflow_block = self.get_workflow_block()
        self.assertTrue(self.database.save_block(workflow_block))
        self.assertIsInstance(self.database.get_blockchain_from_db()[1].transactions[0], WorkflowTransaction)

    def get_block(self):
        pr_key1, pub_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pub_key2 = self.crypto_helper_obj.generate_key_pair()
        self.txn1 = Transaction(pub_key1, pub_key2, "Payload1")
        self.txn1.sign_transaction(self.crypto_helper_obj, pr_key1)
        self.txn1.transaction_hash = self.crypto_helper_obj.hash(self.txn1.get_json())
        return self.blockchain.create_block([self.txn1])

    def get_workflow_block(self):
        pr_key1, pub_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pub_key2 = self.crypto_helper_obj.generate_key_pair()
        payload = {}
        payload['document'] = {}
        payload['in_charge'] = ''
        payload['next_in_charge'] = ''
        payload['workflow_id'] = ''
        payload['processes'] = {}
        payload['permissions'] = {}
        self.txn1 = WorkflowTransaction(pub_key1, pub_key2, payload)
        self.txn1.sign_transaction(self.crypto_helper_obj, pr_key1)
        self.txn1.transaction_hash = self.crypto_helper_obj.hash(self.txn1.get_json())
        return self.blockchain.create_block([self.txn1])

    @classmethod
    def tearDownClass(self):
        # clean up test database
        if os.path.exists(test_db_file):
            os.remove(test_db_file)


if __name__ == '__main__':
    unittest.main()
