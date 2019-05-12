import unittest

from labchain.datastructure.txpool import TxPool
from labchain.datastructure.transaction import Transaction
from mock.cryptoHelper import CryptoHelper

class TxPoolTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def setUp(self):
        crypto_helper_obj = CryptoHelper()
        self.private_key, self.public_key = "s", "r"
        self._txPoolObj = TxPool(crypto_helper_obj)
        self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "a"))
        self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "b"))
        self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "c"))

    def tearDown(self):
        del self._txPoolObj

    def test_add_transaction(self):
        """Test for add transaction, get transaction count and
        get transaction"""
        transaction = Transaction(self.private_key, self.public_key, "d")
        txpool_size = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)
        self.assertEqual(txpool_size + 1, self._txPoolObj.get_transaction_count())
        self.assertEqual(transaction.get_json(), self._txPoolObj.get_transaction().get_json())

    def test_get_transactions(self):
        """Test to get a set of transactions"""
        tx_pool_count = self._txPoolObj.get_transaction_count()
        if tx_pool_count < 2:
            self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "e"))
            self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "f"))
        self.assertFalse(tx_pool_count < 2)
        transactions = self._txPoolObj.get_transactions(tx_pool_count - 1)
        self.assertEqual(len(transactions), tx_pool_count - 1)

    def test_remove_transaction(self):
        """Test remove transaction"""
        transaction = Transaction(self.private_key, self.public_key, "g")
        self._txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        transactions = self._txPoolObj.get_transactions(tx_pool_count)
        self._txPoolObj.return_transactions_to_pool(transactions)
        self.assertTrue(transaction in transactions)
        status = self._txPoolObj.remove_transaction(transaction)
        self.assertEqual(status, True)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        transactions = self._txPoolObj.get_transactions(tx_pool_count)
        self.assertFalse(transaction in transactions)

    def test_return_transactions_to_pool(self):
        """Test for return transactions to pool"""
        transactions = [Transaction(self.private_key, self.public_key, "h"), Transaction(self.private_key, self.public_key, "i"), Transaction(self.private_key, self.public_key, "j")]
        tx_pool_count = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.return_transactions_to_pool(transactions)
        self.assertEqual(status, True)
        transactions_new = self._txPoolObj.get_transactions(tx_pool_count + 3)
        status = any(transaction in transactions for transaction in transactions_new)
        self.assertEqual(status, True)

    def test_singleton(self):
        """Test the single behaviour of the class"""
        transaction = Transaction(self.private_key, self.public_key, "s")
        self._txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        crypto_helper_obj = CryptoHelper()
        txpool = TxPool(crypto_helper_obj)
        self.assertEqual(txpool, self._txPoolObj)
        self.assertEqual(txpool.get_transaction_count(), tx_pool_count)

    def test_get_transaction_count(self):
        """Test the transaction count"""
        transaction = Transaction(self.private_key, self.public_key, "g")
        status = self._txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)
        self.assertEqual(5, self._txPoolObj.get_transaction_count())

    def test_add_transaction_if_not_exist(self):
        """Test adding transaction in txpool only when it is empty"""
        transaction = Transaction(self.private_key, self.public_key, "h")
        status = self._txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)

    def test_get_transaction_by_hash(self):
        """Test adding transaction by hash in txpool"""
        tx_pool_count = self._txPoolObj.get_transaction_count()
        if tx_pool_count < 2:
            self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "e"))
            self._txPoolObj.add_transaction_if_not_exist(Transaction(self.private_key, self.public_key, "f"))
        self.assertFalse(tx_pool_count < 2)
        hash_val = self._txPoolObj.get_transaction_by_hash(self)
        transactions = self._txPoolObj.get_transaction_by_hash(hash_val)

if __name__ == '__main__':
    unittest.main()
