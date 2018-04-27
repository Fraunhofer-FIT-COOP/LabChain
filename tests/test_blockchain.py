#!/usr/bin/env python
import json
import unittest

from blockchain.blockchain import BlockChain
from mock.consensus import Consensus
from mock.txPool import TxPool


class BlockChainComponent(unittest.TestCase):
    """Class of testcases for the Blockchain module"""

    def setUp(self):
        """Setup phase for each testcase"""
        consensus = Consensus()
        txpool = TxPool()
        blockchain = BlockChain(consensus, txpool, None)

        block = blockchain.retrieve_current_block()
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
        txpool = TxPool()
        consensus = Consensus()
        transactions = txpool.get_transactions()
        blockchain_obj = BlockChain(consensus, txpool, None)
        merkle_hash = blockchain_obj.compute_merkle_root(transactions)
        previous_block = blockchain_obj.retrieve_prev_block()
        nonce = Consensus.mine(self.block)
        block_fields = json.dumps({'nr' : 12,
                                   'merkle_hash' : merkle_hash,
                                   'predecessorBlock' : previous_block.hash__,
                                   'nonce' : nonce,
                                   'creator' : self.nodeId,
                                   'transactions' : transactions
                                   })
        status = blockchain_obj.add_block(block_fields)
        self.assertEqual(status, True)

    def test_compute_merkle_tree(self):
        hash = "f75ad0e64820760ddb2c5748c2021c6fbcda832da821aafa5483c0c2faf4cdfb"
        txpool = TxPool()
        consensus = Consensus()
        blockchain_obj = BlockChain(consensus, txpool, None)

        merkle_root = blockchain_obj.compute_merkle_root(self.txns)
        self.assertEqual(merkle_root,hash)

    def test_compute_merkle_tree_false(self):
        hash = "c0c5ebdfa52b975ee46c367313dc34053251bf72b3e21f94622bf66a4d3c2e6c"
        txpool = TxPool()
        consensus = Consensus()
        blockchain_obj = BlockChain(consensus, txpool, None)

        merkle_root = blockchain_obj.compute_merkle_root(self.txns)
        self.assertNotEqual(merkle_root,hash)

if __name__ == '__main__':
    unittest.main()
