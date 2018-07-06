import json
import logging
import math
import sys
import time
from math import log
from random import randint

from labchain.cryptoHelper import CryptoHelper


class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()
        self.max_diff = 5  # Threshold to be defined
        self.kill_mine = 0
        self.last_mine_time_sec = time.time()
        self.expected_mine_freq = 60
        self.diflag = True

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty_2(self, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty):
        if num_of_blocks == 0 or num_of_blocks == 1:
            return int(self.max_diff / 2)

        avg_time = (float(latest_timestamp - earliest_timestamp) / num_of_blocks)
        if avg_time == 0:
            return int(self.max_diff / 2)

        ratio = log(self.expected_mine_freq / avg_time, 2)
        partial_difficulty = ratio * prev_difficulty
        if partial_difficulty < 1:
            return 1
        next = int(math.ceil(partial_difficulty))
        prev = int(math.floor(partial_difficulty))
        current = pow(2, partial_difficulty)
        if pow(2, next) - current < current - pow(2, prev):
            difficulty = next
        else:
            difficulty = prev
        logging.info("difficulty ================ " + str(difficulty))
        return difficulty

    def calculate_difficulty_with_prev(self, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty):
        if num_of_blocks == 0 or num_of_blocks == 1:
            return int(self.max_diff / 2)

        avg_time = (float(latest_timestamp - earliest_timestamp) / num_of_blocks)
        if avg_time == 0:
            return int(self.max_diff / 2)

        ratio = self.expected_mine_freq / avg_time
        prev_max_attemps = pow(2, prev_difficulty)
        current = log(ratio, 2) + float(prev_max_attemps)
        if current <= 0:
            return 1
        partial_difficulty = log(current, 2)
        if partial_difficulty < 1:
            return 1
        difficulty = int(math.floor(partial_difficulty))
        logging.info("difficulty ================ " + str(difficulty))
        return difficulty

    def calculate_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = int(((latest_timestamp - earliest_timestamp) / num_of_blocks))

        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        return self.max_diff - difficulty

        # global difficulty should not be updated, instead return difficulty,
        # because if validate is called during mining, it would update difficulty

    def validate(self, block, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty=-1):
        if self.diflag or prev_difficulty < 1:
            difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        else:
            difficulty = self.calculate_difficulty_with_prev(latest_timestamp, earliest_timestamp, num_of_blocks,
                                                             prev_difficulty)

        logging.debug('#INFO: validate Difficulty: ' + str(difficulty))
        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is validated with result ' + str(
            block_hash[:difficulty] == zeros_array) + ' with hash: ' + str(block_hash))
        logging.info(message)
        return block_hash[:difficulty] == zeros_array

    def mine(self, block, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty=-1):
        if self.diflag or prev_difficulty < 1:
            difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        else:
            difficulty = self.calculate_difficulty_with_prev(latest_timestamp, earliest_timestamp, num_of_blocks,
                                                             prev_difficulty)

        logging.debug('#INFO: mine Difficulty: ' + str(difficulty))
        block.difficulty = difficulty
        start_time = time.time()
        zeros_array = "0" * difficulty
        counter = 0
        block.nonce = randint(0, sys.maxsize)
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
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
        logging.debug('#INFO:Consensus-> Block: ' + str(block) + ' is mined successfully')
        logging.debug("hash = " + str(block_hash))
        # need a boolean return to check if mine got killed
        logging.info(message)
        return True

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(time.time())
