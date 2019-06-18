import json
import logging

class Transaction_Types:
        def __init__(self):
            self.__normal_transaction = 'Normal Transaction'
            self.__contract_creation = 'Contract Creation'
            self.__method_call = 'Method Call'
            self.__contract_termination = 'Contract Termination'
            self.__contract_restoration = 'Contract Restoration'

        @property
        def normal_transaction(self):
            return self.__normal_transaction
        @property
        def contract_creation(self):
            return self.__contract_creation
        @property
        def method_call(self):
            return self.__method_call
        @property
        def contract_termination(self):
            return self.__contract_termination
        @property
        def contract_restoration(self):
            return self.__contract_restoration

class Transaction:
    """Represents a single transaction within the blockchain.
    """

    def __init__(self, sender, receiver, payload, transaction_type, signature=None):
        self.__sender = sender
        self.__receiver = receiver
        self.__payload = payload
        self.__signature = signature
        self.__transaction_type = transaction_type
        self.__transaction_hash = None

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload,
            'transaction_type': self.__transaction_type,
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
        return Transaction(sender=data_dict['sender'], receiver=data_dict['receiver'],
                           payload=data_dict['payload'], transaction_type=data_dict['transaction_type'],
                           signature=data_dict['signature'])

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
            'payload': self.__payload,
            'transaction_type': self.__transaction_type
        })
        self.signature = crypto_helper.sign(private_key, data)

    def __eq__(self, other):
        if not other:
            return None
        return self.sender == other.sender and self.receiver == other.receiver and self.payload == other.payload \
               and self.signature == other.signature

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
            'payload': self.__payload,
            'transaction_type': self.__transaction_type
        })

        if self.__transaction_type == Transaction_Types().method_call:
            methods = json.loads(self.__payload.replace("'",'"'))['methods']
            
            for method in methods:
                try:
                    sender = method['arguments']['sender']
                    if self.__sender != sender:
                        logging.debug('Could not verify transaction. Sender of transaction and ' +
                                        'the sender specified in the method\'s arguments did not match.')
                        return False
                except:
                    logging.debug('Could not verify transaction.')
                    return False

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

    @property
    def transaction_type(self):
        return self.__transaction_type

    @signature.setter
    def signature(self, signature):
        if self.__signature:
            raise ValueError('signature is already set')
        self.__signature = signature

    @transaction_type.setter
    def transaction_type(self, txType):
        if self.__transaction_type:
            raise ValueError('type is already set')
        self.__transaction_type = txType

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


class NoHashError(Exception):
    def __init__(self, message):
        self.message = message
