import unittest

from labchain.datastructure.transaction import Transaction


class TransactionTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def test_from_json(self):
        """Test transaction creation from json"""
        json_string = '{"receiver": "r", "signature": "sig", "payload": "1", "sender": "s"}'
        transaction = Transaction.from_json(json_string)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)

    def test_from_dict(self):
        """Test transaction creation from dict"""
        d = {'sender': 's', 'receiver': 'r', 'payload': '1', 'signature': 'sig'}
        transaction = Transaction.from_dict(d)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)

    def test_set_signature(self):
        """Test for signature setting"""
        transaction = Transaction(sender="s", receiver="r", payload="1")
        self.assertTrue(isinstance(transaction, Transaction))
        transaction.signature = "sig"
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)
        try:
            transaction.signature = "sg"
            self.assertFalse(True)
        except ValueError:
            self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
