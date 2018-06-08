#!/usr/bin/env python
import unittest
import time

from hashlib import sha256 as sha

from labchain.block import Block
from labchain.blockchain import BlockChain
from labchain.consensus import Consensus
from labchain.cryptoHelper import CryptoHelper as crypto
from labchain.transaction import Transaction
from labchain.txpool import TxPool
from labchain.configReader import ConfigReader
from labchain.configReader import ConfigReaderException


class BlockChainComponent(unittest.TestCase):
    """Class of testcases for the Blockchain module"""

    def setUp(self):
        """Setup phase for each testcase"""
        node_config = '../labchain/resources/node_configuration.ini'
        config_reader = ConfigReader(node_config)

        tolerance = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TOLERANCE_LEVEL')
        pruning = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TIME_TO_PRUNE')

        self.consensus = Consensus()
        self.crypto_helper_obj = crypto.instance()
        self.txpool = TxPool(self.crypto_helper_obj)
        self.block_list = []
        self.blockchain = BlockChain(1, tolerance, pruning,
                                     self.consensus, self.txpool,
                                     self.crypto_helper_obj, 10, None, None)

        self.transaction1 = Transaction("Sender1", "Receiver1", "Payload1")
        self.transaction2 = Transaction("Sender2", "Receiver2", "Payload2")
        self.transaction3 = Transaction("Sender3", "Receiver3", "Payload3")
        self.transaction4 = Transaction("Sender4", "Receiver3", "Payload3")

        self.block1 = Block(1, sha("1".encode()).hexdigest(), self.blockchain._node_branch_head,
                            "User1", [self.transaction1, self.transaction2], 101, time.time())

        self.block2 = Block(2, sha("2".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block1.get_json()),
                            "User2", [self.transaction3, self.transaction4], 102, time.time())

        self.block3 = Block(3, sha("3".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block2.get_json()),
                            "User3", [self.transaction1, self.transaction4], 103, time.time())

        self.block4 = Block(4, sha("4".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block3.get_json()),
                            "User4", [self.transaction1, self.transaction3], 104, time.time())

        self.block5 = Block(5, sha("5".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block4.get_json()),
                            "User5", [self.transaction1, self.transaction2], 105, time.time())

        self.block6 = Block(6, sha("6".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block5.get_json()),
                            "User6", [self.transaction3, self.transaction4], 106, time.time())

        self.block7 = Block(7, sha("7".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block6.get_json()),
                            "User7", [self.transaction2, self.transaction4], 107, time.time())

    def test_add_block(self):
        # now block8 has a branch with block 6

        self.block8 = Block(8, sha("8".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block6.get_json()),
                            "User8", [self.transaction2, self.transaction4], 108, time.time())
        self.assertFalse(self.blockchain.add_block(self.block8), "Block is deleted")

        # block 9 has a normal predecessor block 7
        self.block9 = Block(9, sha("9".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block7.get_json()),
                            "User9", [self.transaction2, self.transaction4], 109, time.time())
        self.assertTrue(self.blockchain.add_block(self.block9), "Block is saved")

    def test_switch_to_longest_branch(self):
        # now block8 has a branch with block 6
        self.block8 = Block(8, sha("8".encode()).hexdigest(), self.crypto_helper_obj.hash(self.block6.get_json()),
                            "User8", [self.transaction2, self.transaction4], 108, time.time())

        # we are trying to add a new block in the block chain
        self.blockchain._blockchain[self.crypto_helper_obj.hash(self.block8.get_json())] = self.block8

        # calculating the length of the blockchain before adding new block
        prev_block_length = len(self.blockchain._blockchain.items())

        # calling the switching branch method
        self.blockchain.switch_to_longest_branch()
        # calculating the length of the blockchain after adding new block
        after_block_length = len(self.blockchain._blockchain.items())

        # after branch switching the length of the block should be same
        self.assertEqual(prev_block_length, after_block_length, "Block is deleted")

    def test_calculate_diff(self):
        # blocks added in setup
        blocks, t1, t2 = self.blockchain.calculate_diff()
        self.assertIsNotNone(blocks)
        self.assertIsNotNone(t1)
        self.assertIsNotNone(t2)


    def test_create_block(self):
        # creating new block based on given transaction list
        new_block = self.blockchain.create_block([self.transaction2, self.transaction4])
        self.assertIsNotNone(new_block, "New block Created")

    """def test_send_block_to_neighbour(self):
        block_as_json = self.blockchain.send_block_to_neighbour(self.block1)
        block_as_object = Block.from_json(block_as_json)
        self.assertIsInstance(block_as_object, Block, "Sent the Block information requested by any neighbour")
    """

    def request_block_from_neighbour(self):
        self.assertEqual(1, 2 - 1, "They are equal")


if __name__ == '__main__':
    unittest.main()
