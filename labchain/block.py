import time
import hashlib
import json


class Block(object):
    def __init__(self, block_id=None, timestamp=time.time(), transactions=[],
                 merkle_tree_root=None, predecessor_hash=None, nonce=None,
                 block_creator_id=None):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        block_id : Int
            ID of the block
        timestamp : Timestamp of the block creation
        transactions : List
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
            'transactions': [transaction.get_json() for transaction in self._transactions]
        }

    def get_json(self):
        """Returns the JSON string of the block information"""

        return json.dumps(self.to_dict())

    def get_predecessor_hash(self):
        """Returns the hash of the predecessor block to this block."""

        return self._predecessor_hash

    def get_transactions(self):
        """Returns List of transactions associated with the block"""

        return self._transactions

    def get_block_id(self):
        """Returns the block ID"""

        return self._block_id


class LogicalBlock(Block):
    def __init__(self, block_id=None, transactions=[], predecessor_hash=None,
                 block_creator_id=None, consensus_obj=None, crypto_helper_obj=None):
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

        super(LogicalBlock, self).__init__(block_number=block_number,
                                           transactions=transactions,
                                           predecessor_hash=predecessor_hash,
                                           block_creator_id=block_creator_id)
        self._length_in_chain = None
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

        return (self._block_creator_id == node_id)

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

        block_valid = False
        #  validate signatures, TBD

        transactions = self._transactions
        #  this can be optimized. How?
        for t in transactions:
            if not self._crypto_helper.validate_signature(t):
                break
        else:
            block_valid = True

        #  validate_merkle_tree, TBD
        if not block_valid:
            return False

        #  validate nonce
        block_valid = self._consensus.validate_block(self)

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
            if len(sub_tree) == 1:
                return sub_tree[0]
            else:
                return _merkle_root(sub_tree)

        txn_hash = []
        for tx in self._transactions:
            txn_hash.append(hashlib.sha256(tx.encode('utf-8')).hexdigest())
        return _merkle_root(txn_hash)
