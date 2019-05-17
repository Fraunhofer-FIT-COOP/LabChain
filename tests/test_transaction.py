import unittest
import json
import io
import sys

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from unittest.mock import MagicMock
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper

class TransactionTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def test_to_dict(self):
        """Test transaction creation from json"""
        json_string = '{"receiver": "r", "signature": "sig", "payload": "1", "sender": "s"}'
        transaction = Transaction.from_json(json_string)
        self.assertTrue(isinstance(transaction, Transaction))
        data_dict = transaction.to_dict()
        self.assertEqual(data_dict['sender'], transaction.sender)
        self.assertEqual(data_dict['receiver'], transaction.receiver)
        self.assertEqual(data_dict['payload'], transaction.payload)
        self.assertEqual(data_dict['signature'], transaction.signature)

    def test_get_json(self):
        """Test json string creation from transaction"""
        transaction = Transaction(sender = "s", receiver = "r", payload = "1", signature = "sig")
        self.assertTrue(isinstance(transaction, Transaction))
        json_string = transaction.get_json()
        data_dict = json.loads(json_string)
        self.assertEqual(data_dict['sender'], 's')
        self.assertEqual(data_dict['receiver'], 'r')
        self.assertEqual(data_dict['payload'], '1')
        self.assertEqual(data_dict['signature'], 'sig')


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

    def test_sign_transaction(self):
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd'+
        'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT'+
        'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl'+
        'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        my_transaction = Transaction(sender='real_pub_key', receiver="r", payload="1")
        crypto_helper = CryptoHelper.instance()
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        self.assertFalse(my_transaction.signature == "")

    def test_eq_true(self):
        """Test transaction comparison"""
        my_transaction = Transaction(sender="s", receiver="r", payload="1", signature = "sig")
        other_transaction = my_transaction
        self.assertTrue(my_transaction.__eq__(other_transaction))

    def test_eq_false(self):
        """Test transaction comparison"""
        my_transaction = Transaction(sender="s", receiver="r", payload="1", signature = "sig")
        other_transaction = Transaction(sender=my_transaction.sender, receiver=my_transaction.receiver, payload="2", signature = "othersig")
        self.assertFalse(my_transaction.__eq__(other_transaction))

    def test_validate_transaction_true(self):
        """Test transaction validation"""
        crypto_helper = CryptoHelper.instance()
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd'+
        'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT'+
        'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl'+
        'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        real_pub_key = ('LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowRE'+
        'FRY0RRZ0FFWnQyeUxvOE0xMWp2bnhXanZqTmQ5RmYxNXpDbApwYXlnSm8zcjBDMlpzNHhRNVR4WmlrcHpua1RHTmFW'+
        'dGxQWXE4aE1ZaUZiT2hNUmNWK0lISzJ3dU1BPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')
        real_receiver = "test"
        real_payload = "1"
        true_signature = "OdnESUJkgdmFO2T3JpcS/LX88jNOjCsl/Zspx361rpkSt96TjR66rV8Jw6W4VOtCwYGknfzBPjiMvi0mG27u5Q=="
        my_transaction = Transaction(sender = real_pub_key, receiver = real_receiver, payload = real_payload)
        crypto_helper.sign = MagicMock(return_value = true_signature)
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        self.assertTrue(my_transaction.validate_transaction(crypto_helper))

    def test_validate_transaction_false(self):
        """Test transaction validation"""
        crypto_helper = CryptoHelper.instance()
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd'+
        'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT'+
        'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl'+
        'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        real_pub_key = ('LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowRE'+
        'FRY0RRZ0FFWnQyeUxvOE0xMWp2bnhXanZqTmQ5RmYxNXpDbApwYXlnSm8zcjBDMlpzNHhRNVR4WmlrcHpua1RHTmFW'+
        'dGxQWXE4aE1ZaUZiT2hNUmNWK0lISzJ3dU1BPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')
        fake_receiver = "i_am_fake_receiver"
        real_payload = "1"
        true_signature = "OdnESUJkgdmFO2T3JpcS/LX88jNOjCsl/Zspx361rpkSt96TjR66rV8Jw6W4VOtCwYGknfzBPjiMvi0mG27u5Q=="
        my_transaction = Transaction(sender = real_pub_key, receiver = fake_receiver, payload = real_payload)
        crypto_helper.sign = MagicMock(return_value = true_signature)
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        self.assertFalse(my_transaction.validate_transaction(crypto_helper))

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

    def test_set_transaction_hash(self):
        """Test for transaction_hash setting"""
        transaction = Transaction(sender="s", receiver="r", payload="1")
        self.assertTrue(isinstance(transaction, Transaction))
        transaction.transaction_hash = "123"
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("123", transaction.transaction_hash)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)
        try:
            transaction.transaction_hash = "456"
            self.assertFalse(True)
        except ValueError:
            self.assertTrue(True)

    def test_hash(self):
        """Test the __hash__ function, which returns the hash as an integer"""
        transaction = Transaction(sender="s", receiver="r", payload="1")

        transaction.transaction_hash = '0x123456'
        """run int(transaction.transaction_hash, 16) will get the
        integer representation of 0x123456, which is 1193046"""
        #int_hash = int(transaction.transaction_hash, 16)
        int_hash = 1193046
        self.assertEqual(1193046, transaction.__hash__(), msg='{}'.format(transaction.__hash__()))


    def test_print(self):
        """Test printing transaction details"""
        transaction = Transaction(sender="s", receiver="r", payload="1", signature="sig")
        transaction.transaction_hash = "0x123456"
        capturedOutput = io.StringIO()
        temp = sys.stdout
        sys.stdout = capturedOutput
        transaction.print()
        sys.stdout = temp
        self.assertEqual('Sender Address:   s\n'+
        'Receiver Address: r\n'+
        'Payload:          1\n'+
        'Signature:        sig\n'+
        'Hash:             0x123456\n'
        , capturedOutput.getvalue())



if __name__ == '__main__':
    unittest.main()
