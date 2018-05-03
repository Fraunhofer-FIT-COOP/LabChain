import json
import time

from labchain.transaction import Transaction


class Block:
    """Represents a block in the blockchain."""

    def __init__(self, block_number, merkel_tree_root, predecessor_hash, block_creator_id, transactions=tuple(),
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
        self.block_number = block_number
        self.timestamp = timestamp
        self.merkle_tree_root = merkel_tree_root
        self.predecessor_hash = predecessor_hash
        self.nonce = nonce
        self.block_creator_id = block_creator_id
        self.transactions = transactions

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(
            {
                'nr': self.block_number,
                'timestamp': self.timestamp,
                'merkleHash': self.merkle_tree_root,
                'predecessorBlock': self.predecessor_hash,
                'nonce': self.nonce,
                'creator': self.block_creator_id,
                'transactions': [transaction.get_json() for transaction in self.transactions]
            }
        )

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
