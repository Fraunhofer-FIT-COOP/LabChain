from common.data_types import Block
from common.consensus import Consensus
from datetime import datetime
from unittest import TestCase
import unittest


class Tests(TestCase):

    def test_consensus_mine_true(self):
        consensus = Consensus()
        block = Block(5, datetime.now(), [])
        self.assertTrue(consensus.mine(block) == 0, 'Nonce Value Matches')

    def test_consensus_mine_false(self):
        consensus = Consensus()
        block = Block(5, datetime.now(), [])
        self.assertFalse(consensus.mine(block) == 1, 'Nonce Value Does Not Match')

    def test_consensus_validate_true(self):
        consensus = Consensus()
        block = Block(5, datetime.now(), [])
        self.assertTrue(consensus.validate(block, 0), 'Validation Success')

    def test_consensus_validate_false(self):
        consensus = Consensus()
        block = Block(5, datetime.now(), [])
        self.assertFalse(consensus.validate(block, 1), 'Validation Failure')


if __name__ == '__main__':
    unittest.main()
