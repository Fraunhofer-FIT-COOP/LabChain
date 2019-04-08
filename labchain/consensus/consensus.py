import json
import math
import sys
import time
import logging
import datetime
from random import randint

from labchain.util.cryptoHelper import CryptoHelper


class Consensus:

    def __init__(self):

        self.crypto_helper = CryptoHelper.instance()
        self.max_diff = 5  # Threshold to be defined
        self.min_diff = 1
        self.kill_mine = 0
        self.last_mine_time_sec = time.time()
        self.expected_mine_freq = 30
        self.granular = True
        self.granular_factor = 1
        self.diflag = False
        if not self.granular:
            self.diflag = True
        if self.diflag:
            self.granular = False
        if self.granular:
            self.granular_factor = 4
        self.min_mining_time = time.time()
        self.max_mining_time = 0
        self.avg_mining_time = 0
        self.avg_helper = 0
        self.num_of_mined_blocks = 0
        self.num_of_transactions = 0
        self.avg_diff = 4

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty_with_prev(self, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty,
                                       bits):
        if num_of_blocks == 0 or num_of_blocks == 1:
            return int(self.avg_diff * self.granular_factor)

        avg_time = (float(latest_timestamp - earliest_timestamp) / num_of_blocks)
        if avg_time == 0:
            return int(self.avg_diff * self.granular_factor)
        logging.info("avg time = " + str(avg_time))
        ratio = self.expected_mine_freq / avg_time
        prev_max_attemps = bits * prev_difficulty
        current = math.log(ratio, 2) + float(prev_max_attemps)
        partial_difficulty = float(current) / bits

        if partial_difficulty < self.min_diff * self.granular_factor:
            return self.min_diff * self.granular_factor
        # elif partial_difficulty > self.max_diff * self.granular_factor:
        #   return self.max_diff * self.granular_factor
        # 

        if partial_difficulty <= prev_difficulty:
            difficulty = int(math.floor(partial_difficulty))
        else:
            difficulty = int(math.ceil(partial_difficulty))
        logging.info("avg time=" + str(avg_time) + " prev d=" + str(prev_difficulty) + " difficulty=" + str(difficulty))
        return difficulty

    def calculate_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks):
        difficulty = int(((latest_timestamp - earliest_timestamp) / num_of_blocks))

        if difficulty >= self.max_diff:
            difficulty = self.max_diff - 1
        return self.max_diff - difficulty

        # global difficulty should not be updated, instead return difficulty,
        # because if validate is called during mining, it would update difficulty

    def get_difficulty(self, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty):
        if self.diflag or prev_difficulty < 1:
            difficulty = self.calculate_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks)
        elif not self.granular:
            difficulty = self.calculate_difficulty_with_prev(latest_timestamp, earliest_timestamp, num_of_blocks,
                                                             prev_difficulty, 4)
        else:
            difficulty = self.calculate_difficulty_with_prev(latest_timestamp, earliest_timestamp, num_of_blocks,
                                                             prev_difficulty, 1)
        return difficulty

    def validate(self, block, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty=-1):
        if type(latest_timestamp) is datetime.datetime:
            latest_timestamp = latest_timestamp.timestamp()

        if type(earliest_timestamp) is datetime.datetime:
            earliest_timestamp = earliest_timestamp.timestamp()

        difficulty = self.get_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty)

        logging.debug('#INFO: validate Difficulty: ' + str(difficulty))
        zeros_array = "0" * difficulty
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
            str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce),
                'difficulty': str(block.difficulty)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # Assumed that hash is str
        valid = self.equalZeros(block_hash, zeros_array, difficulty)
        logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is validated with result ' + str(
            valid) + ' with hash: ' + str(block_hash))
        return valid


    def mine(self, block, latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty=-1):
        if type(latest_timestamp) is datetime.datetime:
            latest_timestamp = latest_timestamp.timestamp()

        if type(earliest_timestamp) is datetime.datetime:
            earliest_timestamp = earliest_timestamp.timestamp()

        difficulty = self.get_difficulty(latest_timestamp, earliest_timestamp, num_of_blocks, prev_difficulty)

        logging.debug('#INFO: mine Difficulty: ' + str(difficulty))
        block.difficulty = difficulty
        start_time = time.time()
        zeros_array = "0" * difficulty
        block.nonce = randint(0, sys.maxsize)
        data = {'index': str(block.block_id), 'tree_hash': str(block.merkle_tree_root), 'pre_hash':
                str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce),
                'difficulty': str(block.difficulty)}
        message = json.dumps(data)
        block_hash = self.crypto_helper.hash(message)  # nonce is zero (we need to check that)
        counter = 0
        while not self.equalZeros(block_hash, zeros_array, difficulty):
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
                str(block.predecessor_hash), 'creator': str(block.block_creator_id), 'nonce': str(block.nonce),
                    'difficulty': str(block.difficulty)}
            message = json.dumps(data)
            block_hash = self.crypto_helper.hash(message)
        block.timestamp = time.time()
        self.last_mine_time_sec = start_time
        time_diff = time.time() - start_time
        if time_diff < self.min_mining_time:
            self.min_mining_time = time_diff
        if time_diff > self.max_mining_time:
            self.max_mining_time = time_diff
        self.num_of_mined_blocks = self.num_of_mined_blocks + 1
        self.num_of_transactions = self.num_of_transactions + len(block.transactions)
        self.avg_mining_time = (self.avg_helper + time_diff) / self.num_of_mined_blocks
        self.avg_helper = self.avg_helper + time_diff
        logging.debug('#INFO:Consensus-> Block: ' + str(block.block_id) + ' is mined successfully')
        logging.debug("hash = " + str(block_hash))
        # need a boolean return to check if mine got killed
        return True

    #    Code for updating the difficulty to be implemented by Blockchain component
    #    if self.blocks_counter % self.blocks_threshold  == 0 & self.recalculate == 1:
    #        self.blocks_counter = 0
    #        self.recalculate = 0;
    #        self.difficulty = self.calculate_difficulty(time.time())

    def equalZeros(self, block_hash, zeros_array, difficulty):
        if not self.granular:
            return block_hash[:difficulty] == zeros_array
        bytes_required = int(math.ceil(float(difficulty) / 4))
        if block_hash[:bytes_required - 1] != zeros_array[:bytes_required - 1]:
            return False
        hex_byte = block_hash[bytes_required - 1]
        b = bin(int(hex_byte, 16))[2:]
        zeros = len(b)
        if b == '0':
            zeros -= 1
        zeros = 4 - zeros
        if difficulty - (bytes_required - 1) * 4 > zeros:
            return False
        else:
            return True
