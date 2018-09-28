import unittest
import os

from labchain.datastructure.blockchain import BlockChain
from labchain.consensus.consensus import Consensus
from labchain.util.cryptoHelper import CryptoHelper as crypto
from labchain.datastructure.transaction import Transaction
from labchain.datastructure.txpool import TxPool
from labchain.util.configReader import ConfigReader
from labchain.databaseInterface import Db


class DbTestCase(unittest.TestCase):

    def setUp(self):
        self.database = Db(block_chain_db_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                            '../labchain/resources/labchaindb.sqlite')))
        self.init_components()
        self.create_transactions()
        self.create_blocks()

    def test_create_tables(self):
        self.assertTrue(self.database.create_tables())

    def test_save_block(self):
        self.assertTrue(self.database.save_block(self.block1))
        self.database.get_blockchain_from_db()

    def init_components(self):
        node_config = './labchain/resources/node_configuration.ini'
        config_reader = ConfigReader(node_config)

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
        self.crypto_helper_obj = crypto.instance()
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

    def create_transactions(self):
        pr_key1, pub_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pub_key2 = self.crypto_helper_obj.generate_key_pair()
        pr_key3, pub_key3 = self.crypto_helper_obj.generate_key_pair()
        pr_key4, pub_key4 = self.crypto_helper_obj.generate_key_pair()

        self.txn1 = Transaction(pub_key1, pub_key2, "Payload1")
        self.txn2 = Transaction(pub_key2, pub_key4, "Payload2")
        self.txn3 = Transaction(pub_key3, pub_key1, "Payload3")
        self.txn4 = Transaction(pub_key4, pub_key3, "Payload3")

        self.txn1.sign_transaction(self.crypto_helper_obj, pr_key1)
        self.txn2.sign_transaction(self.crypto_helper_obj, pr_key2)
        self.txn3.sign_transaction(self.crypto_helper_obj, pr_key3)
        self.txn4.sign_transaction(self.crypto_helper_obj, pr_key4)

        self.txn1.transaction_hash=self.crypto_helper_obj.hash(self.txn1.get_json())
        self.txn2.transaction_hash=self.crypto_helper_obj.hash(self.txn2.get_json())
        self.txn3.transaction_hash=self.crypto_helper_obj.hash(self.txn3.get_json())
        self.txn4.transaction_hash=self.crypto_helper_obj.hash(self.txn4.get_json())

    def create_blocks(self):
        self.block1 = self.blockchain.create_block([self.txn1, self.txn2])
        self.block2 = self.blockchain.create_block([self.txn3, self.txn4])
        self.block3 = self.blockchain.create_block([self.txn1, self.txn4])
        self.block4 = self.blockchain.create_block([self.txn1, self.txn3])
        self.block5 = self.blockchain.create_block([self.txn1, self.txn2])
        self.block6 = self.blockchain.create_block([self.txn3, self.txn4])
        self.block7 = self.blockchain.create_block([self.txn2, self.txn4])


if __name__ == '__main__':
    unittest.main()
