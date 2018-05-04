from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response


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

    def add_peer(self, ip_address, port):
        self.peers.append({ip_address: {'port': port}})


class ServerNetworkInterface(NetworkInterface):

    def __init__(self, json_rpc_client, initial_peers,
                 on_block_received_callback,
                 on_transaction_received_callback,
                 get_block_callback,
                 get_transaction_callback,
                 timeout=10, port=6666):
        super().__init__(json_rpc_client, initial_peers, timeout=timeout)
        self.on_block_received_callback = on_block_received_callback
        self.on_transaction_received_callback = on_transaction_received_callback
        self.get_block_callback = get_block_callback,
        self.get_transaction_callback = get_transaction_callback
        self.port = port

    def exchange_peer_lists(self):
        pass

    def advertise_to_peers(self):
        pass

    def poll_exchange_peer_lists(self, poll_interval=10):
        pass

    def start_listening(self):
        run_simple('localhost', self.port, self.application, threaded=True)

    @Request.application
    def application(self, request):
        dispatcher['getPeers'] = self.__handle_get_peers
        dispatcher['advertisePeer'] = self.__handle_advertise_peer
        dispatcher['sendBlock'] = self.__handle_send_block
        dispatcher['sendTransaction'] = self.__handle_send_transaction
        dispatcher['requestBlock'] = self.__handle_request_block
        dispatcher['requestTransaction'] = self.__handle_request_transaction

        response = JSONRPCResponseManager.handle(
            request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    def __handle_get_peers(self):
        return {}

    def __handle_advertise_peer(self, port):
        pass

    def __handle_send_block(self, block_data):
        pass

    def __handle_send_transaction(self, transaction_data):
        pass

    def __handle_request_block(self, block_id):
        pass

    def __handle_request_transaction(self, transaction_hash):
        pass


ClientNetworkInterface = NetworkInterface
