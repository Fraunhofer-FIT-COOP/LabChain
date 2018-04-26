#!/usr/bin/env python
import json
import unittest
from blockchain.merkletree import merkletree


class BlockChainComponent(unittest.TestCase):
    """Class of testcases for the Blockchain module"""

    def setUp(self):
        """Setup phase for each testcase"""

        block = Blockchain.retrieve_current_block()
        self.block = json.loads(block)
        self.nodeId = 'someID'
        self.txns = ["apple", "banana", "orange", "mango", "berry"]
        self.txns.append("pomegranate")


    def test_hold_blocks_potential_branches(self):
        """Testing if the blocks are maintained in a BlockChain
        and all valid chains are being maintained
        """

        pass

    def test_add_block(self):
        """Testing the addition of a new block in the blockchain"""

        transactions = TxPool.get_transactions()
        merkle_hash = MerkleTree.compute_merkle_root(transactions)
        previous_block = Blockchain.retrieve_prev_block()
        nonce = Consensus.mine(self.block)
        block_fields = json.dumps({'nr' : 12,
                                   'merkle_hash' : merkle_hash,
                                   'predecessorBlock' : previous_block.hash__,
                                   'nonce' : nonce,
                                   'creator' : self.nodeId,
                                   'transactions' : transactions
                                   })
        status = Blockchain.add_block(block_fields)
        self.assertEqual(status, True)

    def test_check_transaction_signature(self):
        """Check transaction if they are using valid signatures"""

        for transaction in self.block['transactions']:
            self.assertTrue(Transaction.validate_transaction(transaction))

    def test_compute_merkle_tree(self):
        hash = "f75ad0e64820760ddb2c5748c2021c6fbcda832da821aafa5483c0c2faf4cdfb"
        merkle_tree_object = merkletree()
        merkle_root = merkle_tree_object.compute_merkle_root(self.txns)
        self.assertEqual(merkle_root,hash)

    def test_compute_merkle_tree_false(self):
        hash = "c0c5ebdfa52b975ee46c367313dc34053251bf72b3e21f94622bf66a4d3c2e6c"
        merkle_tree_object = merkletree()
        merkle_root = merkle_tree_object.compute_merkle_root(self.txns)
        self.assertNotEqual(merkle_root,hash)

    def test_block_hash_criteria_satisfied(self):
        """Test if the number of leading zeroes are as configured"""

        status = Consensus.validate(self.block)
        self.assertTrue(status)

    def test_retrieve_block(self):
        """Test if retrieval of block by a node is successful"""

        # Should return correct block since it is in blockchain
        block_id = json.loads(Blockchain.retrieve_prev_block())['nr']
        block = Blockchain.get_block(block_id)
        self.assertIsNotNone(block)

        # Should not return any block since current block is not yet added to the
        # blockchain all nodes have
        block_id = self.block['nr']
        block = Blockchain.get_block(block_id)
        self.assertIsNone(block)

if __name__ == '__main__':
    unittest.main()
