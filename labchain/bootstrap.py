from labchain.networking import BlockDoesNotExistException


class Bootstrapper:
    """Bootstrap the blockchain from other nodes."""

    MAX_BLOCK_REQUEST_RETRIES = 100

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def do_bootstrap(self, blockchain):
        """Initialize a blockchain object with blocks from other nodes."""
        current_block_id = 0
        while True:
            try:
                retries = 0
                while retries < self.MAX_BLOCK_REQUEST_RETRIES:
                    block = self.network_interface.requestBlock(current_block_id)
                    if blockchain.add_block(block):
                        current_block_id += 1
                        break
                    retries += 1
            except BlockDoesNotExistException:
                break
        return blockchain
