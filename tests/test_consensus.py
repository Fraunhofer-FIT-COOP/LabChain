from unittest.mock import MagicMock
from common.data_types import Block
from common.consensus import Consensus
from datetime import datetime
from unittest import TestCase
import unittest


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)
        # For test_show_mine_success
        self.consensus1 = Consensus()
        self.difficulty = 3
        self.nonce_true = 4
        self.test_block_true = Block(0, datetime.now(), "")
        self.test_block_true.pre_hash = ""
        self.test_block_true.creator = ""
        self.encapsulated_block_true = ""
        self.hash_true = ""
        self.hash_false = ""
        self.hash_list_for_nonce_4 = []

    def setup_test_show_mine_success(self):
        self.difficulty = 3
        self.nonce_true = 4
        self.test_block_true = Block(1, datetime.now(), "")
        self.test_block_true.pre_hash = ""
        self.test_block_true.creator = "Patricia"
        self.encapsulated_block_true = str(self.test_block_true.index) + self.test_block_true.pre_hash \
                                       + self.test_block_true.creator + str(self.nonce_true)
        self.hash_true = "00054358392586569542654697954676849367548926706893"
        self.hash_false = "03422354358392586569542654697954676849367548926706893"
        self.hash_list_for_nonce_4 = [self.hash_false, self.hash_false, self.hash_false, self.hash_false,
                                      self.hash_true]

    def test_show_mine_true(self):
        self.setup_test_show_mine_success()

        self.consensus1.difficulty = self.difficulty
        self.consensus1.crypto_helper.hash = MagicMock(side_effect=self.hash_list_for_nonce_4)
        self.consensus1.calculate_difficulty = MagicMock(return_value=self.difficulty)
        returned_nonce = self.consensus1.mine(self.test_block_true)
        self.assertEqual(self.nonce_true, returned_nonce)

    if __name__ == '__main__':
        unittest.main()

    # def test_consensus_mine_true(self):
    #     consensus = Consensus()
    #     block = Block(5, datetime.now(), [])
    #     self.assertTrue(consensus.mine(block) == 0, 'Nonce Value Matches')
    #
    # def test_consensus_mine_false(self):
    #     consensus = Consensus()
    #     block = Block(5, datetime.now(), [])
    #     self.assertFalse(consensus.mine(block) == 1, 'Nonce Value Does Not Match')
    #
    # def test_consensus_validate_true(self):
    #     consensus = Consensus()
    #     block = Block(5, datetime.now(), [])
    #     self.assertTrue(consensus.validate(block, 0), 'Validation Success')
    #
    # def test_consensus_validate_false(self):
    #     consensus = Consensus()
    #     block = Block(5, datetime.now(), [])
    #     self.assertFalse(consensus.validate(block, 1), 'Validation Failure')
