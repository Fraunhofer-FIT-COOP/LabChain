import unittest
import os

from labchain.datastructure.txpool import TxPool
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.blockchain import BlockChain
from labchain.util.configReader import ConfigReader
from labchain.consensus.consensus import Consensus

class TxPoolTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def init_blockchain(self):
        test_resources_dic_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './resources'))
        test_node_config_file = test_resources_dic_path + '/node_configuration.ini'
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

        consensus = Consensus()
        self.block_list = []
        self.blockchain_obj = BlockChain(node_id="nodeId1", tolerance_value=tolerance,
                                     pruning_interval=pruning,
                                     consensus_obj=consensus,
                                     txpool_obj=self._txPoolObj,
                                     crypto_helper_obj=self.crypto_helper_obj,
                                     min_blocks_for_difficulty=min_blocks,
                                     db=None,
                                     q=None)

    def setUp(self):
        self.crypto_helper_obj = CryptoHelper.instance()
        self.private_key1, self.public_key1 = self.crypto_helper_obj.generate_key_pair()
        self.private_key2, self.public_key2 = self.crypto_helper_obj.generate_key_pair()
        self._txPoolObj = TxPool(self.crypto_helper_obj)
        self.init_blockchain()
        t1 = Transaction(self.public_key1, self.public_key2, "a")
        t1.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(t1, self.blockchain_obj)
        t2 = Transaction(self.public_key1, self.public_key2, "b")
        t2.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(t2, self.blockchain_obj)
        t3 = Transaction(self.public_key1, self.public_key2, "c")
        t3.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(t3, self.blockchain_obj)

    def tearDown(self):
        self._txPoolObj._first_time = True

    def test_add_transaction(self):
        """Test for add transaction, get transaction count and
        get transaction"""
        transaction = Transaction(self.public_key1, self.public_key2, "d")
        transaction.sign_transaction(self.crypto_helper_obj, self.private_key1)
        txpool_size = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.add_transaction_if_not_exist(transaction, self.blockchain_obj)
        self.assertEqual(status, True)
        self.assertEqual(txpool_size + 1, self._txPoolObj.get_transaction_count())
        self.assertEqual(transaction.get_json(), self._txPoolObj.get_transaction().get_json())

    def test_get_transactions(self):
        """Test to get a set of transactions"""
        tx_pool_count = self._txPoolObj.get_transaction_count()
        t1 = Transaction(self.public_key1, self.public_key2, "e")
        t1.sign_transaction(self.crypto_helper_obj, self.private_key1)
        t2 = Transaction(self.public_key2, self.public_key1, "f")
        t2.sign_transaction(self.crypto_helper_obj, self.private_key2)
        self._txPoolObj.add_transaction_if_not_exist(t1, self.blockchain_obj)
        self._txPoolObj.add_transaction_if_not_exist(t2, self.blockchain_obj)
        self.assertEqual(3, tx_pool_count)
        self.assertEqual(5, self._txPoolObj.get_transaction_count())
        transactions = self._txPoolObj.get_transactions(3)
        self.assertEqual(len(transactions), 3)
        self.assertEqual(2, self._txPoolObj.get_transaction_count())

    def test_remove_transaction(self):
        """Test remove transaction"""
        transaction = Transaction(self.public_key1, self.public_key2, "g")
        transaction.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(transaction, self.blockchain_obj)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        transactions = self._txPoolObj.get_transactions(tx_pool_count)
        self._txPoolObj.return_transactions_to_pool(transactions, self.blockchain_obj)
        self.assertTrue(transaction in transactions)
        status = self._txPoolObj.remove_transaction(transaction)
        self.assertEqual(status, True)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        transactions = self._txPoolObj.get_transactions(tx_pool_count)
        self.assertFalse(transaction in transactions)

    def test_return_transactions_to_pool(self):
        """Test for return transactions to pool"""
        t1 = Transaction(self.public_key1, self.public_key2, "h")
        t1.sign_transaction(self.crypto_helper_obj, self.private_key1)
        t2 = Transaction(self.public_key1, self.public_key2, "i")
        t2.sign_transaction(self.crypto_helper_obj, self.private_key1)
        t3 = Transaction(self.public_key1, self.public_key2, "j")
        t3.sign_transaction(self.crypto_helper_obj, self.private_key1)
        transactions = [t1, t2, t3]
        tx_pool_count = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.return_transactions_to_pool(transactions, self.blockchain_obj)
        self.assertEqual(status, True)
        transactions_new = self._txPoolObj.get_transactions(tx_pool_count + 3)
        status = any(transaction in transactions for transaction in transactions_new)
        self.assertEqual(status, True)

    def test_singleton(self):
        """Test the single behaviour of the class"""
        transaction = Transaction(self.public_key1, self.public_key2, "s")
        transaction.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(transaction, self.blockchain_obj)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        txpool = TxPool(self.crypto_helper_obj)
        self.assertEqual(txpool, self._txPoolObj)
        self.assertEqual(txpool.get_transaction_count(), tx_pool_count)

    def test_get_transaction_count(self):
        """Test the transaction count"""
        transaction = Transaction(self.public_key1, self.public_key2, "g")
        transaction.sign_transaction(self.crypto_helper_obj, self.private_key1)
        status = self._txPoolObj.add_transaction_if_not_exist(transaction, self.blockchain_obj)
        self.assertTrue(status)
        self.assertEqual(4, self._txPoolObj.get_transaction_count())

    def test_add_transaction_if_not_exist(self):
        """Test adding transaction in txpool only when it is empty"""
        transaction = Transaction(self.public_key1, self.public_key2, "h")
        transaction.sign_transaction(self.crypto_helper_obj, self.private_key1)
        status = self._txPoolObj.add_transaction_if_not_exist(transaction, self.blockchain_obj)
        self.assertTrue(status)

    def test_get_transaction_by_hash(self):
        """Test getting transaction from txpool by hash"""
        tx_pool_count = self._txPoolObj.get_transaction_count()
        t1 = Transaction(self.public_key1, self.public_key2, "e")
        t1.sign_transaction(self.crypto_helper_obj, self.private_key1)
        t2 = Transaction(self.public_key1, self.public_key2, "f")
        t2.sign_transaction(self.crypto_helper_obj, self.private_key1)
        self._txPoolObj.add_transaction_if_not_exist(t1, self.blockchain_obj)
        self._txPoolObj.add_transaction_if_not_exist(t2, self.blockchain_obj)
        self.assertEqual(tx_pool_count, 3)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        self.assertEqual(tx_pool_count, 5)
        hash_val = t1.transaction_hash
        transaction = self._txPoolObj.get_transaction_by_hash(hash_val)[0]
        self.assertEqual(t1, transaction)

if __name__ == '__main__':
    unittest.main()
