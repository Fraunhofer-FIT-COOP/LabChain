import unittest

from labchain.txpool import TxPool
from mock.transaction import Transaction


class TxPoolTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def setUp(self):
        self.__txPoolObj = TxPool()
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("a"))
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("b"))
        self.__txPoolObj.add_transaction_if_not_exist(Transaction("c"))

    def tearDown(self):
        del self.__txPoolObj

    def test_add_transaction(self):
        """Test for add transaction, get transaction count and
        get transaction"""
        transaction = Transaction("d")
        txpool_size = self.__txPoolObj.get_transaction_count()
        status = self.__txPoolObj.add_transaction_if_not_exist(transaction)
        self.assertEqual(status, True)
        self.assertEqual(txpool_size + 1, self.__txPoolObj.get_transaction_count())
        self.assertEqual(transaction.get_json(), self.__txPoolObj.get_transaction().get_json())

    def test_get_transactions(self):
        """Test to get a set of transactions"""
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        if tx_pool_count < 2:
            self.__txPoolObj.add_transaction_if_not_exist(Transaction("e"))
            self.__txPoolObj.add_transaction_if_not_exist(Transaction("f"))
        if tx_pool_count < 2:
            self.assertFalse(True)
        else:
            transactions = self.__txPoolObj.get_transactions(tx_pool_count - 1)
            self.assertEqual(len(transactions), tx_pool_count - 1)

    def test_remove_transaction(self):
        """Test remove transaction"""
        transaction = Transaction("g")
        self.__txPoolObj.add_transaction_if_not_exist(transaction)
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        transactions = self.__txPoolObj.get_transactions(tx_pool_count)
        self.__txPoolObj.return_transactions_to_pool(transactions)
        if transaction in transactions:
            status = self.__txPoolObj.remove_transaction(transaction)
            self.assertEqual(status, True)
            tx_pool_count = self.__txPoolObj.get_transaction_count()
            transactions = self.__txPoolObj.get_transactions(tx_pool_count)
            if transaction in transactions:
                self.assertFalse(True)
        else:
            self.assertFalse(True)

    def test_return_transactions_to_pool(self):
        """Test for return transactions to pool"""
        transactions = [Transaction("g"), Transaction("h"), Transaction("i")]
        tx_pool_count = self.__txPoolObj.get_transaction_count()
        status = self.__txPoolObj.return_transactions_to_pool(transactions)
        self.assertEqual(status, True)
        transactions_new = self.__txPoolObj.get_transactions(tx_pool_count + 3)
        status = any(transaction in transactions for transaction in transactions_new)
        self.assertEqual(status, True)


if __name__ == '__main__':
    unittest.main()
