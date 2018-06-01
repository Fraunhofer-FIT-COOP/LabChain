import json
from datetime import datetime

from labchain.cryptoHelper import CryptoHelper


class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()
        self.difficulty = 1
        self.max_diff = 12  # Threshold to be defined
        self.kill_mine = 0


    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = int((((latest_timestamp - earliest_timestamp).total_seconds()) / num_of_blocks))

        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        self.difficulty = self.max_diff - difficulty

    def validate(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)

        zeros_array = "0" * self.difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        return block_hash[:self.difficulty] == zeros_array

    def mine(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)

        zeros_array = "0" * self.difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
        while block_hash[:self.difficulty] != zeros_array:
            if self.kill_mine == 1:
                self.kill_mine = 0
                break
            block.nonce += 1
            data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
                str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
            message = json.dumps(data)
            block_hash = self.crypto_helper.hash(message)
        block.timestamp = datetime.now()

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(datetime.now())
