#!/usr/bin/env python
import json
import logging
import os
import sys
import unittest
from unittest.mock import MagicMock

from labchain.consensus.consensus import Consensus
from labchain.datastructure.block import LogicalBlock, Block
from labchain.datastructure.blockchain import BlockChain
from labchain.datastructure.transaction import Transaction
from labchain.datastructure.txpool import TxPool
from labchain.util.configReader import ConfigReader
from labchain.util.cryptoHelper import CryptoHelper as crypto

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

test_resources_dic_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './resources'))
test_db_file = test_resources_dic_path + '/labchaindb.sqlite'
test_node_config_file = test_resources_dic_path + '/node_configuration.ini'


class BlockChainComponent(unittest.TestCase):
    """Class of testcases for the Blockchain module"""

    def setUp(self):
        """Setup phase for each testcase"""
        self.init_components()
        self.create_transactions()
        self.create_blocks()

    def test_get_block_range(self):
        # get_block_range doesn't consider genesis block so expected length = 0
        blocks = self.blockchain.get_block_range(0)
        self.assertEqual(len(blocks), 0)

    def test_get_block_by_id(self):
        # fetching first block whose id = 0
        blocks = self.blockchain.get_block_by_id(0)
        for block in blocks:
            self.assertEqual(block._block_id, 0)

    def test_get_block_by_hash(self):
        block_info = json.loads(self.blockchain.get_block_by_hash(self.blockchain._first_block_hash))
        self.assertEqual(block_info['nr'], 0)

    def test_add_block(self):
        """
            Save granular factor before modifying and modify to 0.25
            to speed up test
        """
        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1: LogicalBlock = self.block1
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        # Add block to blockchain
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Block is not added')
        # Check if blockchain has correct length
        blocks = self.blockchain.get_block_range(0)
        self.assertEqual(1, len(blocks))
        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_add_block_already_in_chain(self):
        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1 = LogicalBlock(block_id=23, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=23, transactions=[], nonce=23,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)

        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        # Add both blocks to blockchain
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Block is not added')
        self.assertFalse(self.blockchain.add_block(block1, False),
                         msg='Block was added again')

        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_add_invalid_block(self):
        """
            Tests if an invalid block is added to the blockchain
        """
        self.assertFalse(self.blockchain.add_block(self.block2, False),
                         msg='An invalid block was added!')

    # TODO currently not working!
    def test_add_block_not_logical_block(self):
        """
                    Save granular factor before modifying and modify to 0.25
                    to speed up test
                """
        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1: Block = Block(block_id=42, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=42, transactions=[],
                              nonce=42)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        # Add block to blockchain
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Block is not added')
        # Check if blockchain has correct length
        blocks = self.blockchain.get_block_range(0)
        self.assertEqual(1, len(blocks))
        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_switch_to_longer_blockchain(self):
        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1 = LogicalBlock(block_id=23, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=23, transactions=[], nonce=23,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        block2 = LogicalBlock(block_id=42, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=42, transactions=[], nonce=42,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block2.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block2, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=block1.difficulty)
        # Add both blocks to blockchain
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Block for first branch is not added')
        self.assertTrue(self.blockchain.add_block(block2, False),
                        msg='Block for second branch is not added')

        block3 = None
        for i in range(1, 3):
            block3 = LogicalBlock(block_id=42 + i, merkle_tree_root=None,
                                  predecessor_hash=block2.get_computed_hash(),  # Hash of genesis block
                                  block_creator_id=42, transactions=[],
                                  nonce=42, consensus_obj=self.consensus)
            _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
                self.blockchain.calculate_diff(block3.predecessor_hash)
            # Mine block to get correct Nonce
            self.consensus.mine(block=block3, latest_timestamp=_latest_ts,
                                earliest_timestamp=_earliest_ts,
                                num_of_blocks=_num_of_blocks,
                                min_blocks=_min_blocks,
                                prev_difficulty=block2.difficulty)
            # Add both blocks to blockchain
            self.assertTrue(self.blockchain.add_block(block3, False),
                            msg='Branch is not extended, because block could not be added')
            block2 = block3

        self.assertEqual(self.blockchain.get_block_range()[0].get_computed_hash(),
                         block3.get_computed_hash(),
                         msg='Branch was not switched correctly')

        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_add_orphan(self):
        self.blockchain.request_block_from_neighbour = MagicMock()

        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1 = LogicalBlock(block_id=23, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=23, transactions=[], nonce=23,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Branch is not extended, because block could not be added')

        block2 = LogicalBlock(block_id=42, merkle_tree_root=None,
                              predecessor_hash=block1.get_computed_hash(),
                              # Hash of genesis block
                              block_creator_id=42, transactions=[], nonce=42,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block2.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block2, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=_latest_difficulty)

        self.blockchain._blockchain.pop(block1.get_computed_hash())

        # Try to add second block to blockchain
        self.assertTrue(self.blockchain.add_block(block2, False),
                        msg='Branch is not extended, because block could not be added')

        self.assertEqual(len(self.blockchain._orphan_blocks), 1, msg='Orphan was added correctly')

        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_add_orphan_to_blockchain_when_predecessor_arrives(self):
        self.blockchain.request_block_from_neighbour = MagicMock()

        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1 = LogicalBlock(block_id=23, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=23, transactions=[], nonce=23,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Branch is not extended, because block could not be added')

        block2 = LogicalBlock(block_id=42, merkle_tree_root=None,
                              predecessor_hash=block1.get_computed_hash(),
                              # Hash of genesis block
                              block_creator_id=42, transactions=[], nonce=42,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block2.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block2, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=_latest_difficulty)
        self.assertTrue(self.blockchain.add_block(block2, False),
                        msg='Branch is not extended, because block could not be added')

        block3 = LogicalBlock(block_id=43, merkle_tree_root=None,
                              predecessor_hash=block2.get_computed_hash(),
                              # Hash of genesis block
                              block_creator_id=42, transactions=[], nonce=42,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block3.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block3, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=_latest_difficulty)

        self.blockchain._blockchain.pop(block1.get_computed_hash())
        self.blockchain._blockchain.pop(block2.get_computed_hash())

        # Try to add second block to blockchain
        self.assertTrue(self.blockchain.add_block(block2, False),
                        msg='Branch is not extended, because block could not be added')

        self.assertEqual(len(self.blockchain._orphan_blocks), 1, msg='Orphan was added correctly')

        # Try to add second block to blockchain
        self.assertTrue(self.blockchain.add_block(block3, False),
                        msg='Branch is not extended, because block could not be added')

        self.assertEqual(len(self.blockchain._orphan_blocks), 2, msg='Orphan was added correctly')

        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Branch is not extended, because block could not be added')

        self.assertEqual(len(self.blockchain._orphan_blocks), 0, msg='Orphan was not move to blockchain')

        self.assertEqual(len(self.blockchain._blockchain), 3 + 1, msg='Blockchain has not expected length')

        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    def test_prune_orphans(self):
        self.blockchain.request_block_from_neighbour = MagicMock()

        previous_granular_factor = self.consensus.granular_factor
        self.consensus.granular_factor = 0.25
        block1 = LogicalBlock(block_id=23, merkle_tree_root=None,
                              predecessor_hash='7f42cf7b8e05f7a6c1f6945514c862e36fcf613a7dd14bbabedbc331eb755cbc',
                              # Hash of genesis block
                              block_creator_id=23, transactions=[], nonce=23,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block1.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block1, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=0)
        self.assertTrue(self.blockchain.add_block(block1, False),
                        msg='Branch is not extended, because block could not be added')

        block2 = LogicalBlock(block_id=42, merkle_tree_root=None,
                              predecessor_hash=block1.get_computed_hash(),
                              # Hash of genesis block
                              block_creator_id=42, transactions=[], nonce=42,
                              consensus_obj=self.consensus)
        _latest_ts, _earliest_ts, _num_of_blocks, _min_blocks, _latest_difficulty = \
            self.blockchain.calculate_diff(block2.predecessor_hash)
        # Mine block to get correct Nonce
        self.consensus.mine(block=block2, latest_timestamp=_latest_ts,
                            earliest_timestamp=_earliest_ts,
                            num_of_blocks=_num_of_blocks,
                            min_blocks=_min_blocks,
                            prev_difficulty=_latest_difficulty)

        self.blockchain._blockchain.pop(block1.get_computed_hash())

        # Try to add second block to blockchain
        self.assertTrue(self.blockchain.add_block(block2, False),
                        msg='Branch is not extended, because block could not be added')

        self.assertEqual(len(self.blockchain._orphan_blocks), 1, msg='Orphan was added correctly')

        self.blockchain.prune_orphans()

        self.assertEqual(len(self.blockchain._orphan_blocks), 0, msg='Orphans have not been pruned')

        # Restore granular_factor
        self.consensus.granular_factor = previous_granular_factor

    """
    def test_add_block1(self):
        # now block8 has a branch with block 6

        self.block8 = self.block1 = self.blockchain.create_block([self.txn2, self.txn4])
        self.assertFalse(self.blockchain.add_block(self.block8), "Block is deleted")

        # block 9 has a normal predecessor block 7
        self.block9 = self.block1 = self.blockchain.create_block([self.txn2, self.txn4])
        self.assertTrue(self.blockchain.add_block(self.block9), "Block is saved")
    """

    def test_switch_to_longest_branch(self):
        # now block8 has a branch with block 6
        self.block8 = self.block1 = self.blockchain.create_block([self.txn2, self.txn4])

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
        t1, t2, num_blocks, min_blocks, diff = self.blockchain.calculate_diff()
        self.assertIsNotNone(t1)
        self.assertIsNotNone(t2)
        self.assertIsNotNone(num_blocks)
        self.assertIsNotNone(min_blocks)
        self.assertIsNotNone(diff)

    def test_create_block(self):
        # creating new block based on given transaction list
        new_block = self.blockchain.create_block([self.txn2, self.txn4])
        self.assertIsNotNone(new_block, "New block Created")

    """
    def test_send_block_to_neighbour(self):
        block_as_json = self.blockchain.send_block_to_neighbour(self.block1)
        block_as_object = Block.from_json(block_as_json)
        self.assertIsInstance(block_as_object, Block, "Sent the Block information requested by any neighbour")
    """

    def init_components(self):
        node_config = test_node_config_file
        config_reader = ConfigReader(node_config)

        tolerance = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TOLERANCE_LEVEL')
        pruning = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TIME_TO_PRUNE')
        min_blocks = config_reader.get_config(
            section='MINING',
            option='NUM_OF_BLOCKS_FOR_DIFFICULTY')

        self.consensus = Consensus()
        self.crypto_helper_obj = crypto.instance()
        self.txpool = TxPool(self.crypto_helper_obj)
        self.block_list = []
        self.blockchain = BlockChain(node_id="nodeId1", tolerance_value=tolerance,
                                     pruning_interval=pruning,
                                     consensus_obj=self.consensus,
                                     txpool_obj=self.txpool,
                                     crypto_helper_obj=self.crypto_helper_obj,
                                     min_blocks_for_difficulty=min_blocks,
                                     db=None,
                                     q=None)

    def create_transactions(self):
        pr_key1, pub_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pub_key2 = self.crypto_helper_obj.generate_key_pair()
        pr_key3, pub_key3 = self.crypto_helper_obj.generate_key_pair()
        pr_key4, pub_key4 = self.crypto_helper_obj.generate_key_pair()

        self.txn1 = Transaction(pub_key1, pub_key2, "Payload1")
        self.txn2 = Transaction(pub_key2, pub_key4, "Payload2")
        self.txn3 = Transaction(pub_key3, pub_key1, "Payload3")
        self.txn4 = Transaction(pub_key4, pub_key3, "Payload3")

        self.txn1.sign_transaction(self.crypto_helper_obj, pr_key1)
        self.txn2.sign_transaction(self.crypto_helper_obj, pr_key2)
        self.txn3.sign_transaction(self.crypto_helper_obj, pr_key3)
        self.txn4.sign_transaction(self.crypto_helper_obj, pr_key4)

        self.txn1.transaction_hash = self.crypto_helper_obj.hash(self.txn1.get_json())
        self.txn2.transaction_hash = self.crypto_helper_obj.hash(self.txn2.get_json())
        self.txn3.transaction_hash = self.crypto_helper_obj.hash(self.txn3.get_json())
        self.txn4.transaction_hash = self.crypto_helper_obj.hash(self.txn4.get_json())

    def create_blocks(self):
        self.block1 = self.blockchain.create_block([self.txn1, self.txn2])
        self.block2 = self.blockchain.create_block([self.txn3, self.txn4])
        self.block3 = self.blockchain.create_block([self.txn1, self.txn4])
        self.block4 = self.blockchain.create_block([self.txn1, self.txn3])
        self.block5 = self.blockchain.create_block([self.txn1, self.txn2])
        self.block6 = self.blockchain.create_block([self.txn3, self.txn4])
        self.block7 = self.blockchain.create_block([self.txn2, self.txn4])


if __name__ == '__main__':
    unittest.main()
