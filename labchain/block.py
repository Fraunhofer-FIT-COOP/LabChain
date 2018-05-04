import json
import time

from labchain.transaction import Transaction


class Block:
    """Represents a block in the blockchain."""

    def __init__(self, block_number, merkle_tree_root, predecessor_hash, block_creator_id, transactions=tuple(),
                 nonce=None, timestamp=time.time()):
        """Constructor for Block class

        Args:
            transactions (List): Transactions to form the block

        Class Variables:
            block_number (int): Unique ID for block created
            timestamp (time): Time when block was created
            merkle_tree_root (hash): Hash of Transactions merkle root
            predecessor_hash (hash): Previous Block hash value
            nonce (int): Nonce matching blockchain criteria
            block_creator_id (String): Node ID who created the block
            transactions (List): Transactions in the block

        """
        self.__block_number = block_number
        self.timestamp = timestamp
        self.__merkle_tree_root = merkle_tree_root
        self.__predecessor_hash = predecessor_hash
        self.nonce = nonce
        self.__block_creator_id = block_creator_id
        self.__transactions = tuple(transactions)

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'nr': self.__block_number,
            'timestamp': self.timestamp,
            'merkleHash': self.__merkle_tree_root,
            'predecessorBlock': self.__predecessor_hash,
            'nonce': self.nonce,
            'creator': self.__block_creator_id,
            'transactions': [transaction.get_json() for transaction in self.__transactions]
        }

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Block instance."""
        data_dict = json.loads(json_data)
        return Transaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Block from a data dictionary."""
        return Block(data_dict['nr'], data_dict['merkleHash'], data_dict['predecessorBlock'], data_dict['creator'],
                     [Transaction.from_dict(transaction_dict) for transaction_dict in data_dict['transactions']],
                     data_dict['nonce'], data_dict['timestamp'])

    def __str__(self):
        return str(self.to_dict())

    @property
    def block_number(self):
        return self.__block_number

    @property
    def merkle_tree_root(self):
        return self.__merkle_tree_root

    @property
    def predecessor_hash(self):
        return self.__predecessor_hash

    @property
    def block_creator_id(self):
        return self.__block_creator_id

    @property
    def transactions(self):
        return self.__transactions
