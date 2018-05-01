from labchain.cryptoHelper import CryptoHelper
from unittest import TestCase
import unittest


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_show_hash_true(self):
        #  Values Dumped
        message = {'message': 'Hello World'}
        hash_true = '98be8b9818c2538fd0c476f3ddd0d6b7e3a58ad77be5cef38a74ecdcd9c01ef1'

        helper = CryptoHelper.instance()
        returned_hash = helper.hash(message).hexdigest()
        self.assertEqual(hash_true, returned_hash)

    def test_show_hash_false(self):
        #  Values Dumped
        message = {'message': 'Bye World'}
        hash_false = '98be8b9818c2538fd0c476f3ddd0d6b7e3a58ad77be5cef38a74ecdcd9c01ef1'

        helper = CryptoHelper.instance()
        returned_hash = helper.hash(message).hexdigest()

        self.assertFalse(hash_false == returned_hash)

    def test_show_signature_true(self):
        helper = CryptoHelper.instance()
        public_key, private_key = helper.generate_key_pair()

        message = {'message': 'Hello World'}
        signature_true = helper.sign(private_key, message)

        self.assertTrue(helper.validate(public_key, message, signature_true))

    def test_show_signature_false(self):
        helper = CryptoHelper.instance()
        public_key, private_key = helper.generate_key_pair()

        message_true = {'message': 'Hello World'}
        signature_true = helper.sign(private_key, message_true)

        message_false = {'message': 'Bye World'}

        self.assertFalse(helper.validate(public_key, message_false, signature_true))

    # Is input in json format?
    def test_signature_input_true(self):
        pass

    # Same above.
    def test_validate_input_true(self):
        pass

    # Check if public key is the corresponding public key for the given private key
    def test_key_pairs_match(self):
        pass

    if __name__ == '__main__':
        unittest.main()
