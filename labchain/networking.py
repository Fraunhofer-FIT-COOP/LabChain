class NodeNotAvailableException(Exception):
    pass


class NodeTimeoutException(Exception):
    pass


class TransactionDoesNotExistException(Exception):
    pass


class BlockDoesNotExistException(Exception):
    pass


class NetworkInterface:
    def __init__(self, initial_peers, timeout=10):
        """

        :param initial_peers: List of IP addresses (optional with :port) of the initial peers (at least one).
        """
        self.initial_peers = initial_peers
        self.timeout = timeout

    def sendTransaction(self, transaction):
        pass

    def sendBlock(self, transaction):
        pass

    def requestTransaction(self, transaction_hash):
        pass

    def requestBlock(self, block_id):
        pass


class ServerNetworkInterface(NetworkInterface):

    def __init__(self, initial_peers,
                 on_block_received_callback,
                 on_transaction_received_callback,
                 listen_port=6666,
                 timeout=10):
        super().__init__(initial_peers, timeout)
        self.on_block_received_callback = on_block_received_callback
        self.on_transaction_received_callback = on_transaction_received_callback
        self.listen_port = listen_port,

    def start_listening(self):
        pass


ClientNetworkInterface = NetworkInterface
