import json
import logging
import time
from hashlib import sha256 as sha
from pprint import pformat

from labchain.cryptoHelper import CryptoHelper
from labchain.transaction import Transaction


class Block(object):
    def __init__(self, block_id=None, merkle_tree_root=None,
                 predecessor_hash=None, block_creator_id=None,
                 transactions=[], nonce=0, timestamp=time.time()):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        block_id : Int
            ID of the block
        timestamp : Timestamp of the block creation
        transactions : List (Change to tuple later)
            Transactions to be included in the block
        merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        predecessor_hash : Hash
            Hash of the predecessor block to this block
        nonce : Int
            Value for which block hash satisfies criteria of HashCash
        block_creator_id : String
            ID of the node who created this block

        Attributes
        ----------
        Same as the parameters

        """
        self._block_id = block_id
        self._timestamp = timestamp
        self._transactions = transactions
        self._merkle_tree_root = merkle_tree_root
        self._predecessor_hash = predecessor_hash
        self._nonce = nonce
        self._block_creator_id = block_creator_id

    def to_dict(self):
        """Returns block data as a dictionary."""
        return {
            'nr': self._block_id,
            'timestamp': self._timestamp,
            'merkleHash': self._merkle_tree_root,
            'predecessorBlock': self._predecessor_hash,
            'nonce': self._nonce,
            'creator': self._block_creator_id,
            'transactions': [transaction.to_dict() for transaction in self._transactions]
        }

    def to_json_headers(self):
        """Returns block headers data as a dictionary."""
        return json.dumps({'nr': self._block_id,
                           'merkleHash': self._merkle_tree_root,
                           'predecessorBlock': self._predecessor_hash,
                           'nonce': self._nonce,
                           'creator': self._block_creator_id, })

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Block instance."""
        data_dict = json.loads(json_data)
        return Block.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Block from a data dictionary."""
        return Block(block_id=data_dict['nr'],
                     merkle_tree_root=data_dict['merkleHash'],
                     predecessor_hash=data_dict['predecessorBlock'],
                     block_creator_id=data_dict['creator'],
                     transactions=[Transaction.from_dict(transaction_dict)
                                   for transaction_dict in data_dict['transactions']],
                     nonce=data_dict['nonce'],
                     timestamp=data_dict['timestamp'])

    def __str__(self):
        return pformat(self.to_dict())

    @property
    def block_id(self):
        return self._block_id

    @property
    def merkle_tree_root(self):
        return self._merkle_tree_root

    @property
    def predecessor_hash(self):
        return self._predecessor_hash

    @property
    def block_creator_id(self):
        return self._block_creator_id

    @property
    def transactions(self):
        return self._transactions

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def nonce(self):
        return self._nonce

    @nonce.setter
    def nonce(self, nonce):
        self._nonce = nonce

    def __eq__(self, other):
        """compare blocks
        1) compare all properties"""
        if isinstance(other, Block) or isinstance(other, LogicalBlock):
            return all([self._block_id == other.block_id,
                        self._timestamp == other.timestamp,
                        self._transactions == other.transactions,
                        self._merkle_tree_root == other.merkle_tree_root,
                        self._predecessor_hash == other.predecessor_hash,
                        self._nonce == other.nonce,
                        self._block_creator_id == other.block_creator_id])
        else:
            return False

    def mine_equality(self, other):
        if isinstance(other, Block) or isinstance(other, LogicalBlock):
            return any([self._block_id == other.block_id,
                        any(t in self._transactions for t in other.transactions)])


class LogicalBlock(Block):
    def __init__(self, block_id=None, transactions=[], predecessor_hash=None,
                 block_creator_id=None, merkle_tree_root=None, nonce=0,
                 timestamp=time.time(), consensus_obj=None, crypto_helper_obj=None):
        """Constructor for LogicalBlock, derives properties from the
        placeholder class Block.

        Parameters
        ----------
        block_id : Int
            ID of the block
        transactions : List
            Transactions to be included in the block
        predecessor_hash : Hash
            Hash of the predecessor block to this block
        block_creator_id : String
            ID of the node who created this block
        merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        consensus_obj : Instance of consensus module
        crypto_helper_obj : Instance of cryptoHelper module

        Attributes
        ----------
        _length_in_chain : Int
            Position at which it resides in the node's chain
        _merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        _consensus : Instance of consensus module
        crypto_helper_obj : Instance of cryptoHelper module

        """

        super(LogicalBlock, self).__init__(block_id=block_id,
                                           merkle_tree_root=merkle_tree_root,
                                           predecessor_hash=predecessor_hash,
                                           block_creator_id=block_creator_id,
                                           transactions=transactions, nonce=nonce,
                                           timestamp=timestamp)
        self._length_in_chain = None
        self._crypto_helper = CryptoHelper.instance()
        self._consensus = consensus_obj
        if not self._merkle_tree_root:
            self._merkle_tree_root = self.compute_merkle_root()

    def is_block_ours(self, node_id):
        """Checks to see if the block was created by the node ID specified.

        Parameters
        ----------
        node_id : String
            Node ID against which to check

        Returns
        -------
        Boolean
            True if matches, else False

        """

        return self._block_creator_id == node_id

    def set_block_nonce(self, value):
        """Sets the nonce value for the block"""

        self._nonce = value

    def get_block_pos(self):
        """Returns position at which block resides in the chain"""

        return self._length_in_chain

    def set_block_pos(self, value):
        """Sets the position at which block will reside in chain"""

        self._length_in_chain = value

    def get_computed_hash(self):
        """Gets the hash for the entire block"""

        return self._crypto_helper.hash(self.to_json_headers())

    @staticmethod
    def from_block(block, consensus_obj):
        """Instantiate LogicalBlock from Block"""
        return LogicalBlock.from_dict(block.to_dict(), consensus_obj)

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Block instance."""
        data_dict = json.loads(json_data)
        return LogicalBlock.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict, consesnus_obj=None):
        """Instantiate a LogicalBlock from a data dictionary."""
        return LogicalBlock(block_id=data_dict['nr'],
                            merkle_tree_root=data_dict['merkleHash'],
                            predecessor_hash=data_dict['predecessorBlock'],
                            block_creator_id=data_dict['creator'],
                            transactions=[Transaction.from_dict(transaction_dict)
                                          for transaction_dict in data_dict['transactions']],
                            nonce=data_dict['nonce'],
                            timestamp=data_dict['timestamp'],
                            consensus_obj=consesnus_obj)

    def get_block_obj(self):
        return Block.from_json(super(LogicalBlock, self).get_json())

    def validate_block(self, _latest_timestamp, _earliest_timestamp,
                       _num_of_blocks):
        """Validate the block by checking -
           1. The transaction signatures in the block
           2. The Merkle Tree correctness
           3. The Block Hash with given Nonce to see if it
              satisfies the configured number of zeroes.

        Returns
        -------
        Boolean
            True if valid, False otherwise

        """

        # Validate Transaction signatures
        transactions = self._transactions
        for t in transactions:
            if not t.validate_transaction(self._crypto_helper):
                logging.debug('Invalid transaction: {}'.format(t))
                return False

        # Validate Merkle Tree correctness
        if self.compute_merkle_root() != self._merkle_tree_root:
            logging.debug('Invalid merkle root: {}'.format(t))
            return False

        #  validate nonce
        block_valid = self._consensus.validate(self, _latest_timestamp,
                                               _earliest_timestamp,
                                               _num_of_blocks)

        if not block_valid:
            logging.debug('Invalid block: {}'.format(self))

        return block_valid

    def compute_merkle_root(self):
        """Computes the merkle tree root for all transactions inside the block

        Returns
        -------
        Hash
            Merkle Tree root of the transactions

        """

        def _merkle_root(hashes):
            sub_tree = []
            for i in range(0, len(hashes), 2):
                # If not the last element
                if i + 1 < len(hashes):
                    # Concatenate the hashes and calculate their hash
                    value = str(hashes[i] + hashes[i + 1]).encode(
                        'UTF-8')
                    hash = sha(value).hexdigest()
                else:
                    hash = hashes[i]
                sub_tree.append(hash)
            if len(sub_tree) == 0:
                return None
            elif len(sub_tree) == 1:
                return sub_tree[0]
            else:
                return _merkle_root(sub_tree)

        txn_hashes = []
        for t in self._transactions:
            txn_hashes.append(self._crypto_helper.hash(t.get_json()))
        return _merkle_root(txn_hashes)
