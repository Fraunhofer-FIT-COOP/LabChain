from Crypto.PublicKey import ECC
from labchain.cryptoHelper import CryptoHelper
from unittest import TestCase
import unittest
import json


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_hash_input_false(self):
        message = "Hello World"
        helper = CryptoHelper.instance()
        with self.assertRaises(ValueError):
            helper.hash(message)

    def test_show_hash_true(self):
        #  Values Dumped
        data = {'message': 'Hello World'}
        message = json.dumps(data)
        hash_true = 'a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e'

        helper = CryptoHelper.instance()
        returned_hash = helper.hash(message)
        self.assertEqual(hash_true, returned_hash)

    def test_show_hash_false(self):
        #  Values Dumped
        data = {'message': 'Bye World'}
        message = json.dumps(data)

        hash_false = '98be8b9818c2538fd0c476f3ddd0d6b7e3a58ad77be5cef38a74ecdcd9c01ef1'

        helper = CryptoHelper.instance()
        returned_hash = helper.hash(message)

        self.assertFalse(hash_false == returned_hash)

    def test_show_signature_true(self):
        helper = CryptoHelper.instance()
        private_key, public_key = helper.generate_key_pair()

        data = {'message': 'Hello World'}
        message = json.dumps(data)
        signature_true = helper.sign(private_key, message)

        self.assertTrue(helper.validate(public_key, message, signature_true))

    def test_show_signature_false(self):
        helper = CryptoHelper.instance()
        private_key, public_key = helper.generate_key_pair()

        data = {'message': 'Hello World'}
        message_true = json.dumps(data)
        signature_true = helper.sign(private_key, message_true)

        data = {'message': 'Bye World'}
        message_false = json.dumps(data)

        self.assertFalse(helper.validate(public_key, message_false, signature_true))

    def test_show_validate_true(self):
        helper = CryptoHelper.instance()
        private_key, public_key = helper.generate_key_pair()

        data = {'message': 'Hello World'}
        message = json.dumps(data)
        signature_true = helper.sign(private_key, message)

        self.assertTrue(helper.validate(public_key, message, signature_true))

    def test_show_validate_false(self):
        helper = CryptoHelper.instance()
        private_key, public_key = helper.generate_key_pair()

        data = {'message': 'Hello World'}
        message = json.dumps(data)
        signature_true = helper.sign(private_key, message)

        #  generate a new public key
        public_key_false, private_key_false = helper.generate_key_pair()

        #  tamper with signature
        signature_byte_array = bytearray(signature_true)
        signature_byte_array[0] = (signature_byte_array[0]+1)%256
        signature_false = bytes(signature_byte_array)

        self.assertFalse(helper.validate(public_key, message, signature_false))
        self.assertFalse(helper.validate(public_key_false, message, signature_true))

    # Check if public key is the corresponding public key for the given private key
    def test_key_pairs_match(self):
        helper = CryptoHelper.instance()
        public_key, private_key = helper.generate_key_pair()
        key = ECC.import_key(private_key)
        public_key_true = key.public_key()
        self.assertEqual(public_key_true, ECC.import_key(private_key))
