from Common.data_types import CryptoHelper

class Consensus:

    def __init__(self):
        self.difficulty = self.calculate_difficulty()

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self):
        #   TO-DO:  must be configured somehow
        difficulty = 4
        return difficulty

    def validate(self, block):

        zeros_array = "0" * self.difficulty
        helper = CryptoHelper()
        # Assumed that hash is str
        encapsulated_block = str(block.index) + block.merkleHash + block.pre_hash + block.creator + str(block.nonce)
        block_hash = helper.hash(encapsulated_block)
        return block_hash[0:self.difficulty] == zeros_array

    def mine(self, block):
        difficulty = self.difficulty
        zeros_array = "0" * difficulty
        helper = CryptoHelper()

        #   nonce is zero (we need to check that)
        encapsulated_block = str(block.index) + block.merkleHash + block.pre_hash + block.creator + str(block.nonce)
        block_hash = helper.hash(encapsulated_block)

        while block_hash[:difficulty] != zeros_array:

            block.nonce += 1
            encapsulated_block = str(block.index) + block.merkleHash + block.pre_hash + block.creator + str(block.nonce)
            block_hash = helper.hash(encapsulated_block)

        return block.nonce
