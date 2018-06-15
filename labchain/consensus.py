import json
import math
import sys
import time
import logging
from random import randint

from labchain.cryptoHelper import CryptoHelper


class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()
        self.max_diff = 5  # Threshold to be defined
        self.kill_mine = 0
        self.last_mine_time_sec = time.time()
        self.avg_time_to_mine = 120
        self.min_diff = 1
        self.factor = 100

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty_2(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        if num_of_blocks == 1:
            return int(self.max_diff / 2)
        if latest_timestamp < earliest_timestamp:
            return self.max_diff
        avg_mine_frequency = (latest_timestamp - earliest_timestamp) / num_of_blocks
        difficulty = self.max_diff - int(math.log((avg_mine_frequency * self.factor) / self.avg_time_to_mine))
        if difficulty > self.max_diff:
            difficulty = self.max_diff
        elif difficulty < self.min_diff:
            difficulty = self.min_diff
        return difficulty

    def calculate_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = int(((latest_timestamp - earliest_timestamp) / num_of_blocks))

        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        return self.max_diff - difficulty

        # global difficulty should not be updated, instead return difficulty,
        # because if validate is called during mining, it would update difficulty

    def validate(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        # difficulty = self.calculate_difficulty_2(latest_timestamp, earliest_timestamp, num_of_blocks)

        logging.debug('#INFO: validate Difficulty: ' + str(difficulty))
        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is validated with result ' + str(
            block_hash[:difficulty] == zeros_array) + ' with hash: ' + str(block_hash))
        return block_hash[:difficulty] == zeros_array

    def mine(self, block, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        # difficulty = self.calculate_difficulty_2(latest_timestamp, earliest_timestamp, num_of_blocks)

        logging.debug('#INFO: mine Difficulty: ' + str(difficulty))

        start_time = time.time()
        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
        counter = 0
        block.nonce = randint(0, sys.maxsize)
        while block_hash[:difficulty] != zeros_array:
            if self.kill_mine == 1:
                self.kill_mine = 0
                # need a boolean return to check if mine got killed
                logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' mining process has been killed')
                return False
            block.nonce += 1
            counter = counter + 1
            if counter % 10000 == 0:
                logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is in mining process')
            data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
                str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
            message = json.dumps(data)
            block_hash = self.crypto_helper.hash(message)
        block.timestamp = time.time()
        self.last_mine_time_sec = start_time
        logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is mined successfully')
        # need a boolean return to check if mine got killed
        return True

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(time.time())
