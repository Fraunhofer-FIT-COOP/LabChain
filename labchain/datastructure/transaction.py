import json

from labchain.util.cryptoHelper import CryptoHelper
from labchain.util.publicKeyNameMaping import PublicKeyNamesMapping


class Transaction:
    """Represents a single transaction within the blockchain.
    """

    def __init__(self, sender, receiver, payload, signature=None):
        self.__sender = sender
        self.__receiver = receiver
        self.__payload = payload
        self.__signature = signature
        self.__transaction_hash = None

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload,
            'signature': self.__signature,
        }

    def get_json_with_signature(self):
        """Serialize this instance to a JSON string."""
        return json.dumps({
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload,
            'signature': self.__signature
        }, sort_keys=True)

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps({
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload
        }, sort_keys=True)

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Transaction instance."""
        data_dict = json.loads(json_data)
        t = Transaction.from_dict(data_dict)
        t.transaction_hash = CryptoHelper.instance().hash(t.get_json())
        return t

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Transaction from a data dictionary."""
        t = Transaction(data_dict['sender'], data_dict['receiver'],
                        data_dict['payload'], data_dict['signature'])
        t.transaction_hash = CryptoHelper.instance().hash(t.get_json())
        return t

    def sign_transaction(self, crypto_helper, private_key):
        """
        Passing the arguments for signature with given private key.
        :param private_key: Private key of the signer in the string format.
        :param crypto_helper: Crypto_Helper instance used for signing
        """
        self.signature = crypto_helper.sign(private_key, self.get_json())

    def __eq__(self, other):
        if not other:
            return None
        return (self.sender == other.sender
                and self.receiver == other.receiver
                and self.payload == other.payload
                and self.signature == other.signature)

    def validate_transaction(self, crypto_helper, blockchain) -> bool:
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: Crypto_Helper instance used for validation
        :param blockchain: Blockchain object
        :returns: Receives result of transaction validation.
        """
        return crypto_helper.validate(self.sender, self.get_json(), self.signature)

    def __str__(self):
        dict_with_names = PublicKeyNamesMapping.replace_public_keys_with_names(self.to_dict())
        return str(dict_with_names)

    @property
    def sender(self):
        return self.__sender

    @property
    def receiver(self):
        return self.__receiver

    @property
    def payload(self):
        return self.__payload

    @property
    def signature(self):
        return self.__signature

    @signature.setter
    def signature(self, signature):
        if self.__signature:
            raise ValueError('signature is already set')
        self.__signature = signature

    @property
    def transaction_hash(self):
        return self.__transaction_hash

    @transaction_hash.setter
    def transaction_hash(self, transaction_hash):
        if self.__transaction_hash:
            raise ValueError('transaction_hash is already set')
        self.__transaction_hash = transaction_hash

    def __hash__(self):
        if self.__transaction_hash:
            return int(self.__transaction_hash, 16)
        else:
            raise NoHashError("Transaction has no hash")

    def print(self):
        print('Sender Address:   {}'.format(self.__sender))
        print('Receiver Address: {}'.format(self.__receiver))
        print('Payload:          {}'.format(self.__payload))
        print('Signature:        {}'.format(self.__signature))
        print('Hash:             {}'.format(self.__transaction_hash))


class NoHashError(Exception):
    def __init__(self, message):
        self.message = message
