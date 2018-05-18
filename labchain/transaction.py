import json


class Transaction:
    """Represents a single transaction within the blockchain.
    """

    def __init__(self, sender, receiver, payload, signature=None):
        self.__sender = sender
        self.__receiver = receiver
        self.__payload = payload
        self.__signature = signature

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload,
            'signature': self.__signature
        }

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Transaction instance."""
        data_dict = json.loads(json_data)
        return Transaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Transaction from a data dictionary."""
        return Transaction(data_dict['sender'], data_dict['receiver'],
                           data_dict['payload'], data_dict['signature'])
    #TODO: safe remove
    def get_keys(self):
        private_key, public_key = self._Crypto_Helper.generate_key_pair()

    def sign_transaction(self, crypto_helper, private_key):
        """
        Passing the arguments for signature with given private key.
        :param private_key: Private key of the signer in the string format.
        :param payload: JSON of the data to be signed.
        :param signature: Receeives signed transaction.
        """
        data = json.dumps({
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload
        })
        self.signature = crypto_helper.sign(private_key, data)

    def __eq__(self, other):
        """compare transactions
        1) compare properties"""
        pass

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param public_key: Public key of the signer in the string format.
        :param payload: JSON of the data to be signed.
        :param result: Receeives result of transaction validation.
        """
        data = json.dumps({
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload
        })
        return crypto_helper.validate(self.sender, data, self.signature)

    def __str__(self):
        return str(self.to_dict())

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
