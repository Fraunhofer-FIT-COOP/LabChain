import time
import hashlib
import json

from labchain.transaction import Transaction


class Block(object):
    def __init__(self, block_id=None,
                 merkle_tree_root=None, predecessor_hash=None, block_creator_id=None,
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
        self.__block_id = block_id
        self.timestamp = timestamp
        self.__transactions = transactions
        self.__merkle_tree_root = merkle_tree_root
        self.__predecessor_hash = predecessor_hash
        self.nonce = nonce
        self.__block_creator_id = block_creator_id

    def to_dict(self):
        """Returns block data as a dictionary."""
        return {
            'nr': self.__block_id,
            'timestamp': self.timestamp,
            'merkleHash': self.__merkle_tree_root,
            'predecessorBlock': self.__predecessor_hash,
            'nonce': self.nonce,
            'creator': self.__block_creator_id,
            'transactions': [transaction.to_dict() for transaction in self.__transactions]
        }

    #TODO: method to return block headers for block hash

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
        return Block(data_dict['nr'], data_dict['merkleHash'], data_dict['predecessorBlock'], data_dict['creator'],
                     [Transaction.from_dict(transaction_dict) for transaction_dict in data_dict['transactions']],
                     data_dict['nonce'], data_dict['timestamp'])

    def __str__(self):
        return str(self.to_dict())

    @property
    def block_id(self):
        return self.__block_id

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

    def get_timestamp(self):
        """Returns timestamp of the block"""

        return self.timestamp

    #TODO: block or logical block?
    def __eq__(self, other):
        """compare blocks
        1) compare all properties"""
        pass


class LogicalBlock(Block):
    def __init__(self, block_id=None, transactions=[], predecessor_hash=None,
                 block_creator_id=None, merkle_tree_root=None,
                 consensus_obj=None, crypto_helper_obj=None):
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
                                           transactions=transactions,)
        self._length_in_chain = None
        if not self._merkle_tree_root:
            self._merkle_tree_root = self.compute_merkle_root()
        self._consensus = consensus_obj
        self._crypto_helper = crypto_helper_obj

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

        return self.__block_creator_id == node_id

    def set_block_nonce(self, value):
        """Sets the nonce value for the block"""

        self.nonce = value

    def get_block_pos(self):
        """Returns position at which block resides in the chain"""

        return self._length_in_chain

    def set_block_pos(self, value):
        """Sets the position at which block will reside in chain"""

        self._length_in_chain = value

    def get_computed_hash(self):
        """Gets the hash for the entire block"""

        return self._crypto_helper.hash(self.get_json())

    def validate_block(self):
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
        transactions = self.__transactions
        for t in transactions:
            if not t.validate_signature(self._crypto_helper):
                return False

        # Validate Merkle Tree correctness
        if self.compute_merkle_root() != self.__merkle_tree_root:
            return False

        #  validate nonce
        #block_valid = self._consensus.validate(self, block, )

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
                    value = str(hashes[i] + hashes[i + 1]).encode('utf-8')
                    hash = hashlib.sha256(value).hexdigest()
                else:
                    hash = hashes[i]
                sub_tree.append(hash)
            if len(sub_tree) == 0:
                return None
            elif len(sub_tree) == 1:
                return sub_tree[0]
            else:
                return _merkle_root(sub_tree)

        txn_hash = []
        for tx in self.__transactions:
            txn_hash.append(hashlib.sha256(tx.encode('utf-8')).hexdigest())
        return _merkle_root(txn_hash)
