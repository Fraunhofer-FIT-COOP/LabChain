import unittest

from labchain.cryptoHelper import CryptoHelper
from labchain.txpool import TxPool
from labchain.transaction import Transaction


class TxPoolTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def setUp(self):
        crypto_helper_obj = CryptoHelper.instance()
        self._txPoolObj = TxPool(crypto_helper_obj)
        self._txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "a"))
        self._txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "b"))
        self._txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "c"))

    def tearDown(self):
        del self._txPoolObj

    def test_add_transaction(self):
        """Test for add transaction, get transaction count and
        get transaction"""
        transaction = Transaction("s", "r", "d")
        txpool_size = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)
        self.assertEqual(txpool_size + 1, self._txPoolObj.get_transaction_count())
        self.assertEqual(transaction.get_json(), self._txPoolObj.get_transaction().get_json())

    def test_get_transactions(self):
        """Test to get a set of transactions"""
        tx_pool_count = self._txPoolObj.get_transaction_count()
        if tx_pool_count < 2:
            self._txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "e"))
            self._txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "f"))
        self.assertFalse(tx_pool_count < 2)
        transactions = self._txPoolObj.get_transactions(tx_pool_count - 1)
        self.assertEqual(len(transactions), tx_pool_count - 1)

    def test_remove_transaction(self):
        """Test remove transaction"""
        transaction = Transaction("s", "r", "g")
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
        transactions = [Transaction("s", "r", "h"), Transaction("s", "r", "i"), Transaction("s", "r", "j")]
        tx_pool_count = self._txPoolObj.get_transaction_count()
        status = self._txPoolObj.return_transactions_to_pool(transactions)
        self.assertEqual(status, True)
        transactions_new = self._txPoolObj.get_transactions(tx_pool_count + 3)
        status = any(transaction in transactions for transaction in transactions_new)
        self.assertEqual(status, True)

    def test_singleton(self):
        """Test the single behaviour of the class"""
        transaction = Transaction("s", "r", "s")
        self._txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self._txPoolObj.get_transaction_count()
        crypto_helper_obj = CryptoHelper()
        txpool = TxPool(crypto_helper_obj)
        self.assertEqual(txpool, self._txPoolObj)
        self.assertEqual(txpool.get_transaction_count(), tx_pool_count)


if __name__ == '__main__':
    unittest.main()
