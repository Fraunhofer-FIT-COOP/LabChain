class NodeNotAvailableException(Exception):
    pass


class NodeTimeoutException(Exception):
    pass


class TransactionDoesNotExistException(Exception):
    pass


class BlockDoesNotExistException(Exception):
    pass


class JsonRpcClient:
    def send(self, ip_address, port, data):
        """Convert data to json and send it over the network.

        Return the answer dictionary.
        """
        pass


class NetworkInterface:
    def __init__(self, json_rpc_client, initial_peers, timeout=10):
        """

        :param initial_peers: List of IP addresses (optional with :port) of the initial peers (at least one).
        """
        self.json_rpc_client = json_rpc_client
        self.peers = initial_peers
        self.timeout = timeout

    def sendTransaction(self, transaction):
        pass

    def sendBlock(self, transaction):
        pass

    def requestTransaction(self, transaction_hash):
        pass

    def requestBlock(self, block_id):
        pass

    def add_peer(self, ip_address):
        self.peers.append(ip_address)


class ServerNetworkInterface(NetworkInterface):

    def __init__(self, json_rpc_client, initial_peers,
                 on_block_received_callback,
                 on_transaction_received_callback,
                 timeout=10):
        super().__init__(json_rpc_client, initial_peers, timeout=timeout)
        self.on_block_received_callback = on_block_received_callback
        self.on_transaction_received_callback = on_transaction_received_callback

    def start_exchange_peer_lists(self, poll_interval=10):
        pass

    def start_listening(self, port):
        pass


ClientNetworkInterface = NetworkInterface
