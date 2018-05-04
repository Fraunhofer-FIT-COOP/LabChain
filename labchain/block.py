import time
import hashlib

class Block:
    def __init__(self, predecessor_hash, block_creator_id, transactions,
                 consensus_obj):
        self._timestamp = time.time()
        self._transactions = transactions
        self._merkle_tree_root = self.compute_merkle_root()
        self._predecessor_hash = predecessor_hash
        self._nonce = None
        self._block_creator_id = block_creator_id
        self._length_in_chain = None
        self._consensus = consensus_obj

    def is_block_ours(self, node_id):
        return (self._block_creator_id == node_id)

    def get_json(self):
       pass

    def set_block_nonce(self, value):
        self._nonce = value

    def get_block_pos(self):
        return self._length_in_chain

    def set_block_pos(self, value):
        self._length_in_chain = value

    def get_predecessor_hash(self):
       return self._predecessor_hash

    def get_transactions(self):
        return self._transactions

    def get_computed_hash(self):
        # we must make sure the dictionary is ordered , otherwise we will get inconsistent hashes
        # This is wrong, json dump on self won't run. TBD
        # block_string = json.dump(self, sort_keys=True).encode()
        # return hashlib.sha256(block_string).hexdigest()
        return 'abc'

    def validate_block(self):
        block_valid = False
        #  validate signatures, TBD

        transactions = self._transactions
        #  this can be optimized
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
