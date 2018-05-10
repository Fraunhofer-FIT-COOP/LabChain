from labchain.block import LogicalBlock
import json

TOLERANCE_LEVEL = 6

class BlockChain:
    def __init__(self, consensus_obj, txpool_obj, node_id, crypto_helper_obj):
        self._blockchain = {} # hash : block
        self._orphan_blocks = {} # parent-hash : block
        self._current_branch_heads = []
        self._node_branch_head = None
        self._furthest_branching_point = {"block" : None, "position" : float("inf")}
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
        _curr_block = block

        if _prev_hash in self._blockchain:
            _prev_block = self._blockchain.get(_prev_hash)
            _prev_block_pos = _prev_block.get_block_pos()

            if _prev_hash in self._current_branch_heads:
                self._current_branch_heads.remove(_prev_hash)
            else:
                if _prev_block_pos < self._furthest_branching_point["position"]:
                    self._furthest_branching_point["position"] = _prev_block_pos
                    self._furthest_branching_point["block"] = _prev_block

            _curr_block.set_block_pos(_prev_block_pos + 1)
            self._blockchain[_curr_block_hash] = _curr_block
            self._current_branch_heads.append(_curr_block_hash)

            if _curr_block.is_block_ours(self._node_id):
                self._node_branch_head = _curr_block_hash

            # Remove transactions covered by the block from our TxPool
            self._txpool.remove_transactions(_curr_block.get_transactions())

            # Check recursively if blocks are parent to some orphans
            _parent_hash = _curr_block_hash
            _parent_block = _curr_block
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
            self._orphan_blocks[_prev_hash] = _curr_block
            self.request_block_from_neighbour(_prev_hash)

        self.switch_to_longest_branch()
        return True

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
        if len(self._current_branch_heads) > 1:
            _check_point_pos = self._furthest_branching_point['position']
            _check_point = self._furthest_branching_point['block']
            _check_point_hash = _check_point.get_computed_hash()

            _max_len = 0
            _max_head = None
            for _branch_head_hash in self._current_branch_heads:
                _head = self._blockchain.get(_branch_head_hash)
                _path_len = _head.get_block_pos() - _check_point_pos
                if _path_len > _max_len:
                    _max_len = _path_len
                    _max_head = _head

            if _max_len > TOLERANCE_LEVEL:
                _new_head_hash = _max_head.get_computed_hash()

                # Save all block hashes between furthest branch and head in max chain
                _b_hash = _new_head_hash
                _longest_chain = []
                while _b_hash != _check_point_hash:
                    _longest_chain.append(_b_hash)
                    _b = self._blockchain.get(_b_hash)
                    _b_hash = _b.get_predecessor_hash()
                _longest_chain.append(_check_point_hash)

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

                self._current_branch_heads = [_new_head_hash,]
                self._node_branch_head = _new_head_hash
                self._furthest_branching_point = {"block" : None, "position" : float("inf")}

    def send_block_to_neighbour(self, requested_block_hash):
        return self._blockchain[requested_block_hash]

    def request_block_from_neighbour(self, requested_block_hash):
        # Use networking component to send request
        pass
