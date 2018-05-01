from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

from labchain.singleton import Singleton

import json

@Singleton
class CryptoHelper:

    def __init__(self):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def sign(self, private_key, payload):

        h = self.hash(payload)

        signer = DSS.new(ECC.import_key(private_key), 'fips-186-3')
        signature = signer.sign(h)
        return signature

    def validate(self, public_key, payload, signature):

        h = self.hash(payload)

        verifier = DSS.new(public_key, 'fips-186-3')

        try:
            verifier.verify(h, signature)
            result = True

        except ValueError:
            result = False

        return result

    def generate_key_pair(self):

        key = ECC.generate(curve='P-256')
        private_key = key.export_key(format='PEM')
        public_key = key.public_key()
        return public_key, private_key

    def hash(self, payload):

        string_payload = json.dumps(payload)
        message = string_payload.encode()
        message_hash = SHA256.new(message)
        return message_hash
