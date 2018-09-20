from unittest.mock import MagicMock
from labchain.datastructure.block import Block
from labchain.consensus import Consensus
from datetime import datetime
from unittest import TestCase


class Tests(TestCase):
    def __init__(self, *args):
        super().__init__(*args)

    def test_show_mine_true(self):
        #  Values Dumped
        nonce_true = 4
        hash_true = "00054358392586569542654697954676849367548926706893"
        hash_false = "03422354358392586569542654697954676849367548926706893"
        hash_list_for_nonce_4 = [hash_false, hash_false, hash_false, hash_false, hash_true]
        #  Consensus instance with Mock
        consensus = Consensus()
        consensus.crypto_helper.hash = MagicMock(side_effect=hash_list_for_nonce_4)
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1)

        self.assertEqual(nonce_true, block.nonce)

    def test_show_mine_false(self):
        #  Values Dumped
        nonce_true = 4
        hash_true = "00054358392586569542654697954676849367548926706893"
        hash_false = "03422354358392586569542654697954676849367548926706893"
        hash_list_for_nonce_4 = [hash_false, hash_false, hash_false, hash_true]
        #  Consensus instance with Mock
        consensus = Consensus()
        consensus.crypto_helper.hash = MagicMock(side_effect=hash_list_for_nonce_4)
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())

        consensus.mine(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1)

        self.assertFalse(nonce_true == block.nonce)

    def test_show_validate_true(self):
        #  Values Dumped
        nonce_true = 4
        hash_true = "00054358392586569542654697954676849367548926706893"
        #  Consensus instance with Mock
        consensus = Consensus()
        consensus.crypto_helper.hash = MagicMock(return_value=hash_true)
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        block.nonce = nonce_true

        self.assertTrue(consensus.validate(block,  datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1))

    def test_show_validate_false(self):
        #  Values Dumped
        nonce_false = 4
        hash_false = "03422354358392586569542654697954676849367548926706893"
        #  Consensus instance with Mock
        consensus = Consensus()
        consensus.crypto_helper.hash = MagicMock(return_value=hash_false)
        #  Block Instance
        block = Block(1, None, None, None, [], 0, datetime.now())
        block.nonce = nonce_false
        self.assertFalse(consensus.validate(block, datetime(2007, 12, 6, 15, 29, 52), datetime(2007, 12, 6, 15, 29, 43), 1))
