from labchain.datastructure.block import Block
from labchain.consensus.consensus import Consensus
from datetime import datetime
from unittest import TestCase


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_show_mine_true(self):
        consensus = Consensus()
        block = Block(1, None, None, None, [], 0, datetime.now())
        self.assertTrue(
            consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1, 2))

    def test_show_mine_false(self):
        consensus = Consensus()
        block = Block(1, None, None, None, [], 0, datetime.now())
        consensus.kill_mine = 1
        self.assertFalse(
            consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1, 2, 3))

    def test_show_validate_true(self):
        consensus = Consensus()
        block = Block(1, None, None, None, [], 0, datetime(2007, 12, 6, 15, 29, 52))
        _latest_ts = datetime(2007, 12, 6, 15, 29, 52)
        _earliest_ts = datetime(2007, 12, 6, 15, 29, 43)
        _num_of_blocks = 1
        # Mine block to get correct Nonce
        consensus.mine(block=block, latest_timestamp=_latest_ts,
                       earliest_timestamp=_earliest_ts,
                       num_of_blocks=_num_of_blocks,
                       min_blocks=2,
                       prev_difficulty=0)

        self.assertTrue(consensus.validate(block, _latest_ts, _earliest_ts, 1, 2))

    def test_show_validate_false(self):
        nonce_false = 4
        consensus = Consensus()
        block = Block(1, None, None, None, [], 0, datetime.now())
        block.nonce = nonce_false
        self.assertFalse(
            consensus.validate(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1, 1, 2))
