import time
import hashlib
import json


class Block(object):
    def __init__(self, block_number=None, timestamp=time.time(), transactions=list(),
                 merkle_tree_root=None, predecessor_hash=None, nonce=None,
                 block_creator_id=None):
        self._block_number = block_number
        self._timestamp = timestamp
        self._transactions = transactions
        self._merkle_tree_root = merkle_tree_root
        self._predecessor_hash = predecessor_hash
        self._nonce = nonce
        self._block_creator_id = block_creator_id

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'nr': self._block_number,
            'timestamp': self._timestamp,
            'merkleHash': self._merkle_tree_root,
            'predecessorBlock': self._predecessor_hash,
            'nonce': self._nonce,
            'creator': self._block_creator_id,
            'transactions': [transaction.get_json() for transaction in self._transactions]
        }

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(self.to_dict())

    def get_predecessor_hash(self):
       return self._predecessor_hash

    def get_transactions(self):
        return self._transactions

    def get_block_num(self):
        return self._block_number


class LogicalBlock(Block):
    def __init__(self, block_number, transactions, predecessor_hash,
                 block_creator_id, consensus_obj, crypto_helper_obj):
        super(LogicalBlock, self).__init__(block_number=block_number,
                                           transactions=transactions,
                                           predecessor_hash=predecessor_hash,
                                           block_creator_id=block_creator_id)
        self._length_in_chain = None
        self._consensus = consensus_obj
        self._crypto_helper = crypto_helper_obj
        self._merkle_tree_root = self.compute_merkle_root()

    def is_block_ours(self, node_id):
        return (self._block_creator_id == node_id)

    def set_block_nonce(self, value):
        self._nonce = value

    def get_block_pos(self):
        return self._length_in_chain

    def set_block_pos(self, value):
        self._length_in_chain = value

    def get_computed_hash(self):
        return self._crypto_helper.hash(self.get_json())

    def validate_block(self):
        block_valid = False
        #  validate signatures, TBD

        transactions = self._transactions
        #  this can be optimized. How?
        for t in transactions:
            if not t.validate_signature():
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
        def _merkle_root(hashes):
            sub_tree = []
            for i in range(0, len(hashes), 2):
                # If not the last element
                if i + 1 < len(hashes):
                    # Concatenate the hashes and calculate their hash
                    value = str(hashes[i] + hashes[i+1]).encode('utf-8')
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
