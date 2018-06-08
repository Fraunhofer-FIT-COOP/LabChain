from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from labchain.bootstrap import Bootstrapper, BlockchainInitFailed


class BootrapperTestCase(TestCase):

    def setUp(self):
        self.create_bootstrapper()

    @patch('labchain.block.Block')
    @patch('labchain.block.Block')
    @patch('labchain.block.Block')
    @patch('labchain.blockchain.BlockChain')
    @patch('labchain.networking.NetworkInterface')
    def create_bootstrapper(self, network_interface, blockchain, block1, block2, genesis_block):
        self.network_interface = network_interface
        self.bootstrapper = Bootstrapper(network_interface)
        self.blockchain = blockchain
        self.blockchain.add_block = MagicMock(return_value=True)
        self.blockchain.create_block = MagicMock(return_value=genesis_block)
        self.block1 = block1
        self.block2 = block2
        self.genesis_block = genesis_block

    def _return_two_blocks(self):
        return [self.block1, self.block2]

    def _return_no_blocks_range_case(self):
        return []

    def test_bootstrap_with_existing_blocks(self):
        # given
        self.network_interface.requestBlocksByHashRange = MagicMock(side_effect=self._return_two_blocks)
        # when
        self.bootstrapper.do_bootstrap(self.blockchain)
        # then
        self.assertEqual(2, self.blockchain.add_block.call_count)
        self.blockchain.add_block.assert_has_calls([call(self.block1), call(self.block2)], any_order=False)

    def test_bootstrap_with_no_blocks(self):
        # given
        self.network_interface.requestBlocksByHashRange = MagicMock(side_effect=self._return_no_blocks_range_case)
        # then
        with self.assertRaises(BlockchainInitFailed):
            self.bootstrapper.do_bootstrap(self.blockchain)
