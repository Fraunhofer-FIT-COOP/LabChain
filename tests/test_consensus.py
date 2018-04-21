from common.data_types import Block
from unittest import TestCase


class Consensus:

    def __init__(self, configuration):
        self.configuration = configuration

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def validate(self, block, nonce):
        zeros_array = "0" * (self.configuration + 1)
        counter = 0
        while block.hash[:self.configuration] != zeros_array:
            counter += 1
            block.hash = block.generate_hash()
        if nonce == block.nonce:
            return True
        else:
            return False

    def mine(block, difficulty):
        zeros_array = "0" * (difficulty + 1)
        while block.hash[:difficulty] != zeros_array:
            block.nonce = block.nonce + 1
            block.hash = block.generate_hash()
        return block.nonce
    mine = staticmethod(mine)


class Tests(TestCase):

    def block_test_index(self, block):
        self.assertTrue(self, block.index > -1, 'Index must be a zero or positive integer')

    def consensus_test_configuration(self, consensus):
        self.assertTrue(self, consensus.configuration > 0, 'Configuration must be a positive integer')

    def consensus_mine_test_correctness(self):
        block = Block(5, '11:50:31', [])
        self.assertEqual(self, Consensus.mine(block, 5), 329302932, 'Mining nonce returned value should match')

    def consensus_validate_tests_correctness(self):
        consensus = Consensus(5)
        block = Block(5, '11:50:31', [])
        value = Consensus.mine(block, 5)
        self.assertTrue(self, consensus.validate(block, value))
