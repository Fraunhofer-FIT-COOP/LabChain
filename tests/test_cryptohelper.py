from labchain.cryptoHelper import CryptoHelper
from unittest import TestCase
import unittest


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_show_hash_true(self):
        #  Values Dumped
        message = {'message': 'Hello World'}
        hash_true = '98BE8B9818C2538FD0C476F3DDD0D6B7E3A58AD77BE5CEF38A74ECDCD9C01EF1'

        helper = CryptoHelper.instance()
        returned_hash = helper.hash(message)

        self.assertEqual(hash_true, returned_hash)

    def test_show_hash_false(self):
        pass

    def test_show_signature_true(self):
        pass

    def test_show_signature_false(self):
        pass

    if __name__ == '__main__':
        unittest.main()
