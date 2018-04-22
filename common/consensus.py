from datetime import datetime
from common.data_types import MockCryptoHelper


class Consensus:

    def __init__(self):
        self.difficulty = 1
        self.last_recalculation_timestamp = datetime.now()
        self.blocks_mining_rate = 60  # Threshold to be defined
        self.max_diff = 12  # Threshold to be defined
        self.blocks_threshold = 60
        self.blocks_index = 0

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self, timestamp):
        #
        self.difficulty = ((((timestamp - self.last_recalculation_timestamp).total_seconds()) /
                           self.blocks_mining_rate)).floor()
        self.last_recalculation_timestamp = timestamp
        if self.difficulty >= self.max_diff:
            self.difficulty = self.max_diff - 1
        self.difficulty = self.max_diff - self.difficulty

    def validate(self, block, nonce):
        zeros_array = "0" * self.difficulty
        encapsulated_block = str(block.index) + str(block.tree_hash) + str(block.pre_hash) + str(block.creator) \
                             + str(block.nonce)
        block_hash = MockCryptoHelper.hash(encapsulated_block)  # Assumed that hash is str
        return block_hash[:self.difficulty] == zeros_array and nonce == block.nonce

    def mine(self, block):
        self.blocks_index += 1
        zeros_array = "0" * self.difficulty
        encapsulated_block = str(block.index) + str(block.tree_hash) + str(block.pre_hash) + str(block.creator)\
                             + str(block.nonce)
        block_hash = MockCryptoHelper.hash(encapsulated_block)  # nonce is zero (we need to check that)
        while block_hash[:self.difficulty] != zeros_array:
            block.nonce += 1
            encapsulated_block = (str(block.index) + str(block.tree_hash) + str(block.pre_hash) + str(block.creator)
                                  + str(block.nonce))
            block_hash = MockCryptoHelper.hash(encapsulated_block)
        if self.blocks_index % self.blocks_threshold == 0:
            self.blocks_index = 0
            self.calculate_difficulty(datetime.now())
        return block.nonce
