import json


class Transaction:
    """Represents a single transaction within the blockchain.
    This is a data structure for transaction. The sign_transaction and
    validate_transaction are methods provided by cryptoHelper class.
    Hence pass transaction to cryptoHelper for those functions and only
    set signature according"""

    def __init__(self, sender, receiver, payload, signature=None):
        self._sender = sender
        self._receiver = receiver
        self._payload = payload
        self._signature = signature

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'sender': self._sender,
            'receiver': self._receiver,
            'payload': self._payload,
            'signature': self._signature
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

    def __str__(self):
        return str(self.to_dict())

    @property
    def sender(self):
        return self._sender

    @property
    def receiver(self):
        return self._receiver

    @property
    def payload(self):
        return self._payload

    @property
    def signature(self):
        return self._signature

    @signature.setter
    def signature(self, signature):
        if self._signature:
            raise ValueError('signature is already set')
        self._signature = signature
