from labchain.networking import BlockDoesNotExistException, NoPeersException
from labchain.networking import BlockchainInitFailed


class Bootstrapper:
    """Bootstrap the blockchain from other nodes."""

    MAX_BLOCK_REQUEST_RETRIES = 100

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def do_bootstrap(self, blockchain):
        """Initialize a blockchain object with blocks from other nodes."""
        retries = 0
        while True:
            try:
                blocks = self.network_interface.requestBlocksByHashRange()
            except NoPeersException:
                return blockchain
            for block in blocks:
                blockchain.add_block(block)
            if blocks:
                break
            retries += 1
            if retries == self.MAX_BLOCK_REQUEST_RETRIES:
                raise BlockchainInitFailed()
        return blockchain
