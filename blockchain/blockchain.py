from blockchain.block import Block


class BlockChain:
    def __init__(self, consensus_obj):
        """Constructor for Blockchain class.

        Class Variables:
            __blockchain (dict): Dictionary of blocks currently in chain
                                 key = Hash of the block
                                 value = Block Instance
            __current_branch_heads (dict): Dictionary storing the block
                                 instances currently head of branches.
                                 key = Block instance
                                 value = length of branch from branch point
            __branch_point_hash (String): The hash of the block from where
                                 branching started

        """
        self.__blockchain = {}
        self.__current_branch_heads = {}
        self.__branch_point_hash = None
        self.__consensus_obj = consensus_obj

    def add_block(self, our_own_block=False, block=None):
        """Adds a block to the blockchain.
        Need to validate block first before adding.

        Args:
            our_own_block (Boolean): True if we Block was created by us.
                                     False if Block received from other node.
            block (Block): The Block instance we wish to add to the chain

        Returns:
            Boolean: True for successful addition of block to the chain

        """
        if not isinstance(block, Block):
            del block
            return False

        if not self.validate_block():
            if our_own_block:
                _txns = block.get_transcations()
                self.return_transactions_to_pool(_txns)
            del block
            return False

        _prev_hash = block.get_predecessor_hash()
        if not our_own_block:
            # Check if predecessor block is there in our blockchain head
            if _prev_hash not in self.__blockchain:
                # have to somehow call nodes to get blockchain, needs discussion
                del block
                return False
            _prev_block = self.__blockchain[_prev_hash]
            if _prev_block not in self.__current_branch_heads:
                # We have missed some block updates from node
                # need to get them, needs discussion.
                del block
                return False

        _prev_block = self.__blockchain[_prev_hash]
        _branch_length = self.__current_branch_heads.pop(_prev_block)
        self.__current_branch_heads[block] = _branch_length + 1

        _block_hash = None # TBD: compute hash over here
        self.__blockchain[_block_hash] = block
        self.switch_to_longest_branch()

    def return_transactions_to_pool(self, txns):
        """Return transactions to the transaction pool of node

        Args:
            txns (List): Transactions to return

        """
        pass

    def validate_block(self, block):
        """Validate the block by checking -
           1. Checking the transaction signatures in the block
           2. Checking the Merkle Tree correctness
           3. Checking the Block Hash with given Nonce to see if it
              satisfies the configured number of zeroes.

        Returns:
            Boolean: True for successful validation, False otherwise

        """
        block_valid = False
        #  validate signatures
        transactions = block.get_transcations()
        #  this can be optimized
        for t in transactions:
            if not t.validate_signature():
                break
        else:
            block_valid = True

        #  validate_merkle_tree
        if not block_valid:
            return False

        # validate_merkle_tree
        if not block_valid:
            return False

        #  validate nonce
        block_valid = self.__consensus_obj.validate_block(block)

        return block_valid

    def create_block(self, transactions):
        """Create a new Block for mining.

        Args:
            transactions (List): Transactions to add to the block

        Returns:
            Boolean: True if block creation was successful

        """
        pass

    def switch_to_longest_branch(self):
        """Called after each block addition to the branch, to check if
        branching (if present) has been resolved.

        """

        if len(self.__current_branch_heads) <= 1:
            # No branching occured yet, nothing to do here
            return

        # Branch to switch to.
        _max_head = None

        # Every branch will have length 1, but if some branch has
        # length more than 1 it is a potential longest branch.
        _max_length = 1

        for (_head, _length) in self.__current_branch_heads.items():
            if _length > _max_length:
                _max_head = _head
                _max_length = _length

        if _max_head:
            self.__current_branch_heads.pop(_max_head)
            for (_block, _length) in self.__current_branch_heads.items():
                __prev_block_hash = None
                _curr_block = _block
                while self.__branch_point_hash != __prev_block_hash:
                    _prev_block_hash = _curr_block.get_predecessor_hash()
                    _curr_block.return_transactions()
                    del _curr_block
                    _curr_block = self.__blockchain[_prev_block_hash]
            self.__current_branch_heads = {_max_head: 0, }
            self.__branch_point_hash = None

    def compute_merkle_root(self):
        pass
