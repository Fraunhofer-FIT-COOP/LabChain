from labchain.networking import NoPeersException, NoBlockExistsInRange


class BlockchainInitFailed(Exception):
    pass


class Bootstrapper:
    """Bootstrap the blockchain from other nodes."""

    MAX_BLOCK_REQUEST_RETRIES = 100

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def do_bootstrap(self, blockchain):
        """Initialize a blockchain object with blocks from other nodes."""
        retries = 0
        while True:
            if retries == self.MAX_BLOCK_REQUEST_RETRIES:
                raise BlockchainInitFailed()
            retries += 1
            try:
                blocks = self.network_interface.requestBlocksByHashRange()
            except NoPeersException:
                return blockchain
            except NoBlockExistsInRange:
                continue
            # traverse reverse because the first block is the last element and vice versa
            for block in reversed(blocks):
                blockchain.add_block(block)
            if blocks:
                break

        return blockchain
