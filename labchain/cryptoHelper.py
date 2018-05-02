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

        h = self.__hash(payload)

        signer = DSS.new(ECC.import_key(private_key), 'fips-186-3')
        signature = signer.sign(h)
        return signature

    def validate(self, pub_key, payload, signature):

        h = self.__hash(payload)

        public_key = ECC.import_key(pub_key)

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
        public_key = key.public_key().export_key(format='PEM')
        return private_key, public_key

    def __hash(self, payload):
        message = payload.encode()
        message_hash = SHA256.new(message)
        return message_hash


    def hash(self, payload):

        real_payload = self.__unpack_payload(payload)

        hash_object = self.__hash(real_payload)
        return hash_object.hexdigest()

    def __unpack_payload(self, payload):
        payload_dict = json.loads(payload)
        sorted_payload = sorted(payload_dict)
        real_payload = ""
        for i in sorted_payload:
            real_payload += payload_dict[i]

        return real_payload
