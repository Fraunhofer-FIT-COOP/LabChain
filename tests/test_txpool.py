import unittest

from labchain.txpool import TxPool
from labchain.transaction import Transaction
from mock.cryptoHelper import CryptoHelper


class TxPoolTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def setUp(self):
        crypto_helper_obj = CryptoHelper()
        self.__txPoolObj = TxPool(crypto_helper_obj)
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "a"))
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "b"))
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "c"))

    def tearDown(self):
        del self.__txPoolObj

    def test_add_transaction(self):
        """Test for add transaction, get transaction count and
        get transaction"""
        transaction = Transaction("s", "r", "d")
        txpool_size = self.__txPoolObj.get_transaction_count()
        status = self.__txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)
        self.assertEqual(txpool_size + 1, self.__txPoolObj.get_transaction_count())
        self.assertEqual(transaction.get_json(), self.__txPoolObj.get_transaction().get_json())

    def test_get_transactions(self):
        """Test to get a set of transactions"""
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        if tx_pool_count < 2:
            self.__txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "e"))
            self.__txPoolObj.add_transaction_if_not_exist(Transaction("s", "r", "f"))
        self.assertFalse(tx_pool_count < 2)
        transactions = self.__txPoolObj.get_transactions(tx_pool_count - 1)
        self.assertEqual(len(transactions), tx_pool_count - 1)

    def test_remove_transaction(self):
        """Test remove transaction"""
        transaction = Transaction("s", "r", "g")
        self.__txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        transactions = self.__txPoolObj.get_transactions(tx_pool_count)
        self.__txPoolObj.return_transactions_to_pool(transactions)
        self.assertTrue(transaction in transactions)
        status = self.__txPoolObj.remove_transaction(transaction)
        self.assertEqual(status, True)
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        transactions = self.__txPoolObj.get_transactions(tx_pool_count)
        self.assertFalse(transaction in transactions)

    def test_return_transactions_to_pool(self):
        """Test for return transactions to pool"""
        transactions = [Transaction("s", "r", "h"), Transaction("s", "r", "i"), Transaction("s", "r", "j")]
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        status = self.__txPoolObj.return_transactions_to_pool(transactions)
        self.assertEqual(status, True)
        transactions_new = self.__txPoolObj.get_transactions(tx_pool_count + 3)
        status = any(transaction in transactions for transaction in transactions_new)
        self.assertEqual(status, True)

    def test_singleton(self):
        """Test the single behaviour of the class"""
        transaction = Transaction("s", "r", "s")
        self.__txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        crypto_helper_obj = CryptoHelper()
        txpool = TxPool(crypto_helper_obj)
        self.assertEqual(txpool, self.__txPoolObj)
        self.assertEqual(txpool.get_transaction_count(), tx_pool_count)


if __name__ == '__main__':
    unittest.main()
