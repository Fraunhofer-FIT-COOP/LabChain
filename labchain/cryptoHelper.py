from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

from labchain.singleton import Singleton


@Singleton
class CryptoHelper:

    # Must add singleton feature
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
            print("The message is authentic.")
            result = True

        except ValueError:
            print("The message is not authentic.")
            result = False

        return result

    def generate_key_pair(self):
        key = ECC.generate(curve='P-256')
        private_key = key.export_key(format='PEM')
        public_key = key.public_key()
        return private_key, public_key

    def hash(self, payload):

        message = payload.encode()
        hash = SHA256.new(message)
        return hash