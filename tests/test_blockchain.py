#!/usr/bin/env python
import unittest
from hashlib import sha256 as sha

from labchain.block import Block
from labchain.blockchain import BlockChain
from labchain.consensus import Consensus
from labchain.cryptoHelper import CryptoHelper as crypto
from labchain.transaction import Transaction
from labchain.txpool import TxPool


class BlockChainComponent(unittest.TestCase):
    """Class of testcases for the Blockchain module"""

    def setUp(self):
        """Setup phase for each testcase"""
        consensus = Consensus()
        txpool = TxPool()
        self.blockchain = BlockChain(consensus, txpool, None)
        self.block_list = []
        # self.blockchain = BlockChain(1, 2, 3400, Consensus, TxPool, crypto)

        self.transaction1 = Transaction("Sender1", "Receiver1", "Payload1")

        self.transaction2 = Transaction("Sender2", "Receiver2", "Payload2")

        self.transaction3 = Transaction("Sender3", "Receiver3", "Payload3")

        self.transaction4 = Transaction("Sender4", "Receiver3", "Payload3")

        self.block1 = Block(1, sha(1).hexdigest(), None, "User1", [self.transaction1, self.transaction2], 101)

        self.block2 = Block(2, sha(2).hexdigest(), crypto.hash(self.block1.get_json()), "User2",
                            [self.transaction3, self.transaction4], 102)

        self.block3 = Block(3, sha(3).hexdigest(), crypto.hash(self.block2.get_json()), "User3",
                            [self.transaction1, self.transaction4], 103)

        self.block4 = Block(4, sha(4).hexdigest(), crypto.hash(self.block3.get_json()), "User4",
                            [self.transaction1, self.transaction3], 104)

        self.block5 = Block(5, sha(5).hexdigest(), crypto.hash(self.block4.get_json()), "User5",
                            [self.transaction1, self.transaction2], 105)

        self.block6 = Block(6, sha(6).hexdigest(), crypto.hash(self.block5.get_json()), "User6",
                            [self.transaction3, self.transaction4], 106)

        self.block7 = Block(7, sha(7).hexdigest(), crypto.hash(self.block6.get_json()), "User7",
                            [self.transaction2, self.transaction4], 107)

    def test_add_block(self):
        # now block8 has a branch with block 6
        self.block8 = Block(8, sha(8).hexdigest(), crypto.hash(self.block6.get_json()), "User8",
                            [self.transaction2, self.transaction4], 108)
        self.assertFalse(self.blockchain.add_block(self.block8), "Block is deleted")

        # block 9 has a normal predecessor block 7
        self.block9 = Block(9, sha(9).hexdigest(), crypto.hash(self.block7.get_json()), "User9",
                            [self.transaction2, self.transaction4], 109)
        self.assertTrue(self.blockchain.add_block(self.block9), "Block is saved")

    def test_switch_to_longest_branch(self):
        # now block8 has a branch with block 6
        self.block8 = Block(8, sha(8).hexdigest(), crypto.hash(self.block6.get_json()), "User8",
                            [self.transaction2, self.transaction4], 108)

        # we are trying to add a new block in the block chain
        self.blockchain._blockchain[crypto.hash(self.block8.get_json())] = self.block8

        # calculating the length of the blockchain before adding new block
        prev_block_length = len(self.blockchain._blockchain.items())

        # calling the switching branch method
        self.blockchain.switch_to_longest_branch()
        # calculating the length of the blockchain after adding new block
        after_block_length = len(self.blockchain._blockchain.items())

        # after branch switching the length of the block should be same
        self.assertEqual(prev_block_length, after_block_length, "Block is deleted")

    def test_create_block(self):
        # creating new block based on given transaction list
        new_block = self.blockchain.create_block([self.transaction2, self.transaction4])
        self.assertIsNotNone(new_block, "New block Created")

    def test_send_block_to_neighbour(self):
        block_as_json = self.blockchain.send_block_to_neighbour(self.block1)
        block_as_object = Block.from_json(block_as_json)
        self.assertIsInstance(block_as_object, Block, "Sent the Block information requested by any neighbour")

    def request_block_from_neighbour(self):
        self.assertEqual(1, 2 - 1, "They are equal")


if __name__ == '__main__':
    unittest.main()
