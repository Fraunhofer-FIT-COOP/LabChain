import logging

from labchain.network.networking import NoPeersException, NoBlockExistsInRange

logger = logging.getLogger(__name__)


class BlockchainInitFailed(Exception):
    pass


class Bootstrapper:
    """Bootstrap the blockchain from other nodes."""

    MAX_BLOCK_REQUEST_RETRIES = 100

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def do_bootstrap(self, blockchain):
        """Initialize a blockchain object with blocks from other nodes.
        """
        retries = 0
        while True:
            if retries == self.MAX_BLOCK_REQUEST_RETRIES:
                raise BlockchainInitFailed()
            retries += 1
            try:
                blocks = self.network_interface.requestBlocksByHashRange()
            except NoPeersException:
                logger.info('No peers available for bootstrapping. Starting from scratch...')
                return blockchain
            except NoBlockExistsInRange:
                logger.info('No blocks have been mined yet. Starting from scratch...')
                return blockchain
            # traverse reverse because the first block is the last element and vice versa
            logger.info('Received {} blocks from peers. Adding them now...'.format(len(blocks)))
            for block in reversed(blocks):
                blockchain.add_block(block)

            if len(blocks) > 0:
               break

        return blockchain
