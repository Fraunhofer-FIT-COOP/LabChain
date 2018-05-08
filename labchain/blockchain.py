from labchain.block import LogicalBlock
import json

CHECKPOINT_SIZE = 6

class BlockChain:
    def __init__(self, consensus_obj, txpool_obj, node_id, crypto_helper_obj):
        self._blockchain = {} # hash : block
        self._orphan_blocks = {} # parent-hash : block
        self._current_branch_heads = []
        self._node_branch_head = None
        self._last_checkpoint = None
        self._consensus = consensus_obj
        self._txpool = txpool_obj
        self._crypto_helper = crypto_helper_obj
        self._node_id = node_id

        # Create a very first initial block, hardcoded in all nodes
        # TBD

    def add_block(self, block):
        if not block.validate_block():
            if block.is_block_ours(self._node_id):
                _txns = block.get_transcations()
                self._txpool.return_transactions_to_pool(_txns)
            del block
            return False

        _prev_hash = block.get_predecessor_hash()
        _curr_block_hash = block.get_computed_hash()

        if _prev_hash in self._blockchain:
            # predecessor present in Blockchain
            if _prev_hash in self._current_branch_heads:
                # Does not create a new branch
                self._current_branch_heads.remove(_prev_hash)

            _curr_head = self._blockchain[_prev_hash]
            block.set_block_pos(_curr_head.get_block_pos() + 1)
            self._blockchain[_curr_block_hash] = block
            self._current_branch_heads.append(_curr_block_hash)

            if block.is_block_ours(self._node_id):
                self._node_branch_head = _curr_block_hash

            # Remove transactions covered by the block from our TxPool
            self._txpool.remove_transactions(block.get_transactions())

            # Check if block is parent to some orphans
            _parent_hash = _curr_block_hash
            _parent_block = block
            while _parent_hash in self._orphan_blocks:
                _block = self._orphan_blocks[_parent_hash]
                self._txpool.remove_transactions(_block.get_transactions())
                _this_block_hash = _block.get_computed_hash()
                _block.set_block_pos(_parent_block.get_block_pos() + 1)
                self._blockchain[_this_block_hash] = _block
                _parent_hash = _this_block_hash
                _parent_block = _block

        else:
            # Put block in orphan pool, query predecessor block
            self._orphan_blocks[_curr_block_hash] = block
            self.request_block_from_neighbour(_prev_hash)

        self.switch_to_longest_branch()

    def create_block(self, transactions):
        _curr_head = self._blockchain[self._node_branch_head]
        _new_block_num = _curr_head.get_block_num() + 1
        new_block = LogicalBlock(block_number=_new_block_num,
                                 predecessor_hash=self._node_branch_head,
                                 block_creator_id=self._node_id,
                                 transactions=transactions,
                                 consensus_obj=self._consensus,
                                 crypto_helper_obj=self._crypto_helper)
        return new_block

    def switch_to_longest_branch(self):
        _checkpoint = self._blockchain.get(self._last_checkpoint)
        _max_len = 0
        _max_head = None

        if len(self._current_branch_heads) > 1:
            # Branching has occured, shit!
            # Find the maximum sized branch
            for _branch_head_hash in self._current_branch_heads:
                _head = self._blockchain.get(_branch_head_hash)
                _path_len = _head.get_block_pos() - _checkpoint.get_block_pos()
                if _path_len > _max_len:
                    _max_len = _path_len
                    _max_head = _head

            if _max_len > CHECKPOINT_SIZE:
                _new_head_hash = _max_head.get_computed_hash()

                # Save all block hashes between checkpoint and head in max chain
                _b_hash = _new_head_hash
                _longest_chain = []
                while _b_hash != self._last_checkpoint:
                    _longest_chain.append(_b_hash)
                    _b = self._blockchain.get(_b_hash)
                    _b_hash = _b.get_predecessor_hash()
                _longest_chain.append(self._last_checkpoint)

                # Remove all other branches
                self._current_branch_heads.remove(_new_head_hash)
                for _head in self._current_branch_heads:
                    _b_hash = _head
                    while _b_hash not in _longest_chain:
                        _b = self._blockchain.pop(_b_hash)
                        if _b.is_block_ours(self._node_id):
                            _txns = _b.get_transcations()
                            self._txpool.return_transactions_to_pool(_txns)
                        _b_hash = _b.get_predecessor_hash()
                        del _b

                self._current_branch_heads = [_new_head_hash]
                self._node_branch_head = _new_head_hash
        else:
            # Branching didn't occur yet
            _max_head = self._blockchain.get(self._current_branch_heads[0])
            _max_len = _max_head.get_block_pos() - _checkpoint.get_block_pos()

        if _max_len > CHECKPOINT_SIZE:
            i = 0
            _new_checkpoint = _max_head
            while i < CHECKPOINT_SIZE:
                _new_checkpoint_hash = _new_checkpoint.get_predecessor_hash()
                _new_checkpoint = self._blockchain.get(_new_checkpoint_hash)
                i += 1
            self._last_checkpoint = _new_checkpoint_hash

    def send_block_to_neighbour(self, requested_block_hash):
        return self._blockchain[requested_block_hash]

    def request_block_from_neighbour(self, requested_block_hash):
        # Use networking component to send request
        pass
