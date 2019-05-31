from labchain.datastructure.block import Block
from labchain.consensus.consensus import Consensus
from datetime import datetime
from unittest import TestCase


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_show_mine_true(self):
        #  Values Dumped
        hash_true = "00054358392586569542654697954676849367548926706893"
        hash_false = "03422354358392586569542654697954676849367548926706893"
        hash_list_for_nonce_4 = [hash_false, hash_false, hash_false, hash_true]
        #  Consensus instance with Mock
        consensus = Consensus()
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        self.assertTrue(consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1))

    def test_show_mine_false(self):
        #  Values Dumped
        hash_true = "00054358392586569542654697954676849367548926706893"
        hash_false = "03422354358392586569542654697954676849367548926706893"
        hash_list_for_nonce_4 = [hash_false, hash_false, hash_false, hash_true]
        #  Consensus instance with Mock
        consensus = Consensus()
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        consensus.kill_mine = 1
        self.assertFalse(
            consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1, 3))

    def test_show_validate_true(self):
        #  Values Dumped
        nonce_true = 2106696302847050147
        hash_true = "00054358392586569542654697954676849367548926706893"
        #  Consensus instance with Mock
        consensus = Consensus()
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime(2007, 12, 6, 15, 29, 52))
        _latest_ts = datetime(2007, 12, 6, 15, 29, 52)
        _earliest_ts = datetime(2007, 12, 6, 15, 29, 43)
        _num_of_blocks = 1
        # Mine block to get correct Nonce
        consensus.mine(block=block, latest_timestamp=_latest_ts,
                       earliest_timestamp=_earliest_ts,
                       num_of_blocks=_num_of_blocks,
                       prev_difficulty=0)

        self.assertTrue(consensus.validate(block, _latest_ts, _earliest_ts, 1))

    def test_show_validate_false(self):
        #  Values Dumped
        nonce_false = 4
        hash_false = "03422354358392586569542654697954676849367548926706893"
        #  Consensus instance with Mock
        consensus = Consensus()
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        block.nonce = nonce_false
        self.assertFalse(
            consensus.validate(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1, 2))
