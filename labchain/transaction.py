import json


class Transaction:
    """Represents a single transaction within the blockchain."""

    def __init__(self, sender, receiver, payload, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.signature = signature

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'payload': self.payload,
            'signature': self.signature,
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
        return Transaction(data_dict['sender'], data_dict['receiver'], data_dict['payload'], data_dict['signature'])

    def __str__(self):
        return str(self.to_dict())
