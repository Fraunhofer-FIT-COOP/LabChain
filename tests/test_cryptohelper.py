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
        pass

    def test_show_signature_false(self):
        pass

    # Is input in json format?
    def test_signature_input_true(self):
        pass

    # Same above.
    def test_validate_input_true(self):
        pass

    if __name__ == '__main__':
        unittest.main()
