from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

from labchain.singleton import Singleton
from labchain.utility import Utility

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

        h = self.__hash(payload)                                        # Hash the payload
        signer = DSS.new(ECC.import_key(private_key), 'fips-186-3')     # Get the signature object
        signature = signer.sign(h)                                      # Sign the hash
        return signature

    def validate(self, pub_key, payload, signature):

        h = self.__hash(payload)                            # Hash the payload
        public_key = ECC.import_key(pub_key)                # Get the public key object using public key string
        verifier = DSS.new(public_key, 'fips-186-3')        # Create a signature object

        try:
            verifier.verify(h, signature)                   # Check if the signature is verified
            result = True

        except ValueError:
            result = False

        return result

    def generate_key_pair(self):

        key = ECC.generate(curve='P-256')                       # Create ECC key object
        private_key = key.export_key(format='PEM')              # Get the string of private key
        public_key = key.public_key().export_key(format='PEM')  # Get the string of public key
        return private_key, public_key

    def __hash(self, payload):
        message = payload.encode()          # Encode string for hashing
        message_hash = SHA256.new(message)  # Hash using SHA256 scheme
        return message_hash


    def hash(self, payload):

        real_payload = self.__unpack_payload(payload)   # Get the real payload to be hashed
        hash_object = self.__hash(real_payload)         # Hash the payload
        return hash_object.hexdigest()                  # Return hex representation of the hash

    def __unpack_payload(self, payload):
        real_payload = ""

        if not Utility.is_json(payload):
            real_payload = {'message': 'Payload is not json'}
            return real_payload

        payload_dict = json.loads(payload)  # Get JSON string
        sorted_payload = sorted(payload_dict)  # Get the sorted list of keys

        for i in sorted_payload:
            real_payload += payload_dict[i]  # Concatenate all values according to sorted keys

        return real_payload
