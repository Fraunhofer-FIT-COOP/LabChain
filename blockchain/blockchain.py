from blockchain.block import Block


class BlockChain:
    def __init__(self):
        # __blockchain is a dictionary containing the blocks in chain.
        # key = hash of the block, value = Block instance
        self.__blockchain = {}

        # Dictionary storing the instances of the Block class which are
        # currently at head of each of the branches being maintained.
        # key= Block instance, value= Length of branch from branch point
        self.__current_branch_heads = {}

        # The point in chain from where branching started
        self.__branch_point_hash = None

    def add_block_received(self):
        # Add bock received from some other node, validate first
        pass

    def add_block_created(self, block):
        # Add block created by this node to the chain
        if not self.validate_block():
            block.return_transactions()
            del block
        block_hash = None  # have to compute hash here
        self.__blockchain[block_hash] = block
        pass

    def validate_block(self):
        pass

    def create_block(self, transactions):
        pass

    def switch_to_longest_branch(self):
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
