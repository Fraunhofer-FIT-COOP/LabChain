from datetime import datetime
from common.data_types import CryptoHelper


class Consensus:

    def __init__(self):
        self.difficulty = 1
        self.last_block_timestamp = datetime.now()
        self.difficulty_threshold_range = 0.09  # Threshold to be defined
        self.max_diff = 12  # Threshold to be defined

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self, timestamp):
        #   TO-DO:  must be configured somehow
        self.difficulty = (((timestamp - self.last_block_timestamp).timestamp()) / self.difficulty_threshold_range)
        self.last_block_timestamp = timestamp
        self.difficulty = self.difficulty % self.max_diff
        self.difficulty = self.max_diff - self.difficulty

    def validate(self, block):

        zeros_array = "0" * self.difficulty
        helper = CryptoHelper()  # Assumed that hash is str
        encapsulated_block = str(block.index) + block.merkleHash + block.pre_hash + block.creator + str(block.nonce)
        block_hash = helper.hash(encapsulated_block)
        return block_hash[:self.difficulty] == zeros_array

    def mine(self, block):

        zeros_array = "0" * self.difficulty
        helper = CryptoHelper()  # nonce is zero (we need to check that)
        encapsulated_block = str(block.index) + block.tree_hash + block.pre_hash + block.creator + str(block.nonce)
        block_hash = helper.hash(encapsulated_block)
        while block_hash[:self.difficulty] != zeros_array:
            block.nonce += 1
            encapsulated_block = str(block.index) + block.merkleHash + block.pre_hash + block.creator + str(block.nonce)
            block_hash = helper.hash(encapsulated_block)
        self.calculate_difficulty(block.timestamp)
        return block.nonce
