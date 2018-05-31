from datetime import datetime

from labchain.block import LogicalBlock


class BlockChain:
    def __init__(self, node_id, tolerance_value, pruning_interval,
                 consensus_obj, txpool_obj, crypto_helper_obj):
        """Constructor for BlockChain

        Parameters
        ----------
        node_id : String
            ID of the node running the blockchain
        tolerance_value : Int
            Length required by the longest chain to be switched to
        pruning_interval : Int
            Time given in hours till which the orphan blocks will be stored
        consensus_obj : Instance of consensus module
        txpool_obj : Instance of txpool module
        crypto_helper_obj : Instance of cryptoHelper module

        Attributes
        ----------
        _node_id : String
            ID of the node running the blockchain
        _blockchain : Dictionary
            Dictionary of blocks in our blockchain
            key = block hash, value = LogicalBlock instance
        _orphan_blocks : Dictionary
            Dictionary of blocks whose predecessor block is not in our chain
            key = predecessor block hash, value = LogicalBlock instance
        _current_branch_heads : List
            List of the block hashes, which are branch heads maintained by the node
        _node_branch_head : Hash value
            Hash value of the branch head this node is following
        _furthest_branching_point : Dictionary
            Information about the point where earliest branching happened in chain
            key = block instance of branching point, value = position in the chain
        _tolerance_level : Int
            Length required by the longest chain to be switched to
        _pruning_interval : Int
            Number of seconds orphan blocks are stored before being deleted
        _consensus : Instance of the consensus module
        _txpool : Instance of the txpool module
        _crypto_helper : Instance of cryptoHelper module

        """

        self._node_id = node_id
        self._blockchain = {}
        self._orphan_blocks = {}
        self._current_branch_heads = []
        self._node_branch_head = None
        self._furthest_branching_point = {"block": None, "position": float("inf")}
        self._tolerance_level = tolerance_value
        self._pruning_interval = pruning_interval * 3600
        self._consensus = consensus_obj
        self._txpool = txpool_obj
        self._crypto_helper = crypto_helper_obj

        # Create the very first Block, add it to Blockchain
        # This should be part of the bootstrap/initial node only
        # TODO: genesis block has id 0, implemet genesis if not done#
        # already changed bid from 1 to 0
        _first_block = LogicalBlock(block_id=0, crypto_helper_obj=crypto_helper_obj)
        _first_block.set_block_pos(0)
        _first_block_hash = _first_block.get_computed_hash()
        self._blockchain[_first_block_hash] = _first_block
        self._node_branch_head = _first_block_hash
        self._current_branch_heads = [_first_block_hash, ]

    def get_block(self, block_id):
        #TODO: return a list of blocks from all branches
        pass

    def get_block_by_hash(self, block_hash):
        #TODO: return a block corresponding to hash
        pass

    def get_transaction(self, transaction_hash):
        # TODO: return a transaction from main branch
        """tuple with 1st element as transaction and 2nd element as block_hash"""
        pass

    def calculate_diff(self):
        """Calculate the nth block and timestamps"""
        #TODO:get last nth block its time stamp and time stamp og last block
        #returns tuple(n, time1, timen)
        pass

    def add_block(self, block):
        """Finds correct position and adds the new block to the chain.
        If block predecessor not found in chain, stores block as an orphan.

        Parameters
        ----------
        block : LogicalBlock instance
            The block instance to be added to the chain.

        Returns
        -------
        Boolean
            Returns True if block is saved as orphan or in the chain.
            Return False if block validation fails and it is deleted.

        """
        #TODO: convertz to logical block
        if not block.validate_block():
            if block.is_block_ours(self._node_id):
                _txns = block.transactions
                self._txpool.return_transactions_to_pool(_txns)
            del block
            return False

        _prev_hash = block.predecessor_hash
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
            self._txpool.remove_transactions(_curr_block.transactions)

            # Check recursively if blocks are parent to some orphans
            _parent_hash = _curr_block_hash
            _parent_block = _curr_block
            while _parent_hash in self._orphan_blocks:
                _block = self._orphan_blocks[_parent_hash]
                self._txpool.remove_transactions(_block.transactions)
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
        """Creates a new LogicalBlock instance.

        Parameters
        ----------
        transactions : List
            Transactions to be associated with the block

        Returns
        -------
        new_block : LogicalBlock instance
            The New Block created from the transactions given

        """

        _curr_head = self._blockchain[self._node_branch_head]
        _new_block_id = _curr_head.block_id + 1
        new_block = LogicalBlock(block_id=_new_block_id,
                                 predecessor_hash=self._node_branch_head,
                                 block_creator_id=self._node_id,
                                 transactions=transactions,
                                 consensus_obj=self._consensus,
                                 crypto_helper_obj=self._crypto_helper)
        return new_block

    def switch_to_longest_branch(self):
        """Functionality to switch to the longest chain among all the
        chains currently maintained by blockchain.
        Switches only if the length of one of the chains is more than
        the tolerance level defined.

        """

        if len(self._current_branch_heads) == 1:
            # No Branching happened yet, nothing to do here
            return

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

        if _max_len > self._tolerance_level:
            _new_head_hash = _max_head.get_computed_hash()

            # Save all block hashes between furthest branch and head in max chain
            _b_hash = _new_head_hash
            _longest_chain = []
            while _b_hash != _check_point_hash:
                _longest_chain.append(_b_hash)
                _b = self._blockchain.get(_b_hash)
                _b_hash = _b.predecessor_hash
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
                    _b_hash = _b.predecessor_hash
                    del _b

            self._current_branch_heads = [_new_head_hash, ]
            self._node_branch_head = _new_head_hash
            self._furthest_branching_point = {"block": None, "position": float("inf")}

    def prune_orphans(self):
        _curr_time = datetime.now()
        for _hash in self._orphan_blocks:
            _block = self._orphan_blocks[_hash]
            _block_creation_time = datetime.fromtimestamp(_block.timestamp)
            _time_passed = (_curr_time - _block_creation_time).total_seconds()
            if _time_passed >= self._pruning_interval:
                self._orphan_blocks.pop(_hash)
                del _block

    def send_block_to_neighbour(self, requested_block_hash):
        """Sends the Block information requested by any neighbour.

        Parameters
        ----------
        requested_block_hash : Hash
            Hash value of the block requested.

        Returns
        -------
        block_info : Json structure
            The Json of Block which was requested
            None if Block was not found in node's chain.

        """

        block_info = None
        _req_block = self._blockchain.get(requested_block_hash, None)
        if _req_block:
            block_info = _req_block.get_json()
        return block_info

    def request_block_from_neighbour(self, requested_block_hash):
        """Requests a block from other nodes connected with.

        Parameters
        ----------
        requested_block_hash : Hash
            Hash of the block requested by the node.

        """
        pass
