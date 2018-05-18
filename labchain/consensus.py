import json
from datetime import datetime

from labchain.cryptoHelper import CryptoHelper

#TODO add abort flag to mine func

class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()

        self.difficulty = 1
        self.last_recalculation_timestamp = datetime.now()
        self.time_to_mine_blocks_threshold = 60  # Threshold to be defined
        self.max_diff = 12  # Threshold to be defined
        self.blocks_threshold = 60
        self.blocks_counter = 0
        self.recalculate = 0

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self, timestamp):
        difficulty = ((((timestamp - self.last_recalculation_timestamp).total_seconds()) /
                       self.time_to_mine_blocks_threshold)).floor()
        self.last_recalculation_timestamp = timestamp
        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        difficulty = self.max_diff - difficulty
        return difficulty

    def validate(self, block, nonce):
        # will receive 2 timestamps and number of blocks for calculating diff
        nonce = block.nonce #TODO remove nonce in mtheod sign
        zeros_array = "0" * self.difficulty
        data = {'index': str(block.index), 'tree_hash': str(block.tree_hash), 'pre_hash':
            str(block.pre_hash), 'creator': str(block.creator), 'nonce': str(block.nonce),
                'timestamp': str(block.timestamp)}
        message = json.dumps(data)

        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        return block_hash[:self.difficulty] == zeros_array and nonce == block.nonce

    def mine(self, block):
        # will receive 2 timestamps and number of blocks for calculating diff
        #
        self.blocks_counter += 1
        zeros_array = "0" * self.difficulty
        data = {'index': str(block.index), 'tree_hash': str(block.tree_hash), 'pre_hash':
            str(block.pre_hash), 'creator': str(block.creator), 'nonce': str(block.nonce),
                'timestamp': str(block.timestamp)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
        while block_hash[:self.difficulty] != zeros_array:
            block.nonce += 1
            data = {'index': str(block.index), 'tree_hash': str(block.tree_hash), 'pre_hash':
                str(block.pre_hash), 'creator': str(block.creator), 'nonce': str(block.nonce),
                    'timestamp': str(block.timestamp)}
            message = json.dumps(data)
            block_hash = self.crypto_helper.hash(message)
        block.timestamp = datetime.now()

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(datetime.now())
