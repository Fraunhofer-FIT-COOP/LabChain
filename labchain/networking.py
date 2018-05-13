import json
import random
import time

import requests
from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from labchain.block import Block


class NodeNotAvailableException(Exception):
    pass


class NodeTimeoutException(Exception):
    pass


class TransactionDoesNotExistException(Exception):
    pass


class BlockDoesNotExistException(Exception):
    pass


class JsonRpcClient:
    """Handle outgoing JSON-RPC calls."""

    def __init__(self):
        self.id_counter = 0

    def send(self, ip_address, port, method, params=tuple()):
        """Convert data to json and send it over the network.

        Return the answer dictionary.
        """
        url = 'http://{}:{}/'.format(ip_address, port)
        headers = {'content-type': 'application/json'}
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": self.id_counter,
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers).json()
        self.id_counter += 1
        return response['result']


class NetworkInterface:
    """Basic network interface to be used by clients."""

    def __init__(self, json_rpc_client, initial_peers):
        """

        :param initial_peers: List of IP addresses (optional with :port) of the initial peers (at least one).
        """
        self.json_rpc_client = json_rpc_client
        self.peers = initial_peers

    def sendTransaction(self, transaction):
        pass

    def sendBlock(self, transaction):
        pass

    def requestTransaction(self, transaction_hash):
        pass

    def requestBlock(self, block_id):
        """Request a single block by block ID."""
        shuffled_peer_ips = self.__get_shuffled_peers()
        for peer_ip in shuffled_peer_ips:
            peer_port = self.peers[peer_ip]['port']
            block_data = self.json_rpc_client.send(peer_ip, peer_port, 'requestBlock', [block_id])
            if block_data:
                return Block.from_dict(block_data)
        return None

    def add_peer(self, ip_address, port):
        """Add a single peer to the peer list."""
        self.peers.update({ip_address: {'port': port}})

    def __get_shuffled_peers(self):
        """Retrieve a shuffled list of peer IP addresses."""
        peer_ips = self.peers.keys()
        random.shuffle(peer_ips)
        return peer_ips


class ServerNetworkInterface(NetworkInterface):
    """Advanced network interface for additional server-to-server communication."""

    def __init__(self, json_rpc_client, initial_peers,
                 on_block_received_callback,
                 on_transaction_received_callback,
                 get_block_callback,
                 get_transaction_callback, port=6666):
        """
        :param json_rpc_client: A JsonRpcClient instance.
        :param initial_peers: A dict structured like {'<ip1>': {'port': <port1>}, ...}.
        :param on_block_received_callback: A callable accepting a Block instance as argument.
        :param on_transaction_received_callback: A callable accepting a Transaction instance as argument.
        :param get_block_callback: A callable that gets a block ID and returns the corresponding Block instance or None.
        :param get_transaction_callback: A callable that gets a transaction hash and returns the corresponding
                                            Transaction instance or None.
        :param port: The port number to listen on.
        """
        super().__init__(json_rpc_client, initial_peers)
        self.on_block_received_callback = on_block_received_callback
        self.on_transaction_received_callback = on_transaction_received_callback
        self.get_block_callback = get_block_callback
        self.get_transaction_callback = get_transaction_callback
        self.port = port

    def exchange_peer_lists(self):
        new_peers = {}
        for peer in self.peers:
            port = self.peers[peer]['port']
            response = self.json_rpc_client.send(peer, port, 'getPeers')
            for new_peer in response:
                new_peers[new_peer] = response[new_peer]['port']
        for new_peer in new_peers:
            self.add_peer(new_peer, new_peers[new_peer])

    def advertise_to_peers(self):
        for peer in self.peers:
            port = self.peers[peer]['port']
            self.json_rpc_client.send(peer, port, 'advertisePeer', [self.port])

    def poll_exchange_peer_lists(self, poll_interval=10):
        while True:
            self.exchange_peer_lists()
            time.sleep(poll_interval)

    def start_listening(self):
        """Start listening for incoming HTTP JSON-RPC calls."""
        run_simple('localhost', self.port, self.application, threaded=True)

    @Request.application
    def application(self, request):
        """Define the JSON-RPC callbacks and handle an incoming request."""
        dispatcher['getPeers'] = self.__handle_get_peers
        dispatcher['advertisePeer'] = self.__handle_advertise_peer
        dispatcher['sendBlock'] = self.__handle_send_block
        dispatcher['sendTransaction'] = self.__handle_send_transaction
        dispatcher['requestBlock'] = self.__handle_request_block
        dispatcher['requestTransaction'] = self.__handle_request_transaction

        # insert IP address of peer if advertise peer is called
        request_body_dict = json.loads(request.data.decode())
        if request_body_dict['method'] == 'advertisePeer':
            if 'params' not in request_body_dict:
                request_body_dict['params'] = [6666]
            request_body_dict['params'].insert(0, request.remote_addr)
        request.data = json.dumps(request_body_dict)

        response = JSONRPCResponseManager.handle(
            request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    def __handle_get_peers(self):
        return self.peers

    def __handle_advertise_peer(self, remote_address, port):
        self.add_peer(remote_address, port)
        return True

    def __handle_send_block(self, block_data):
        pass

    def __handle_send_transaction(self, transaction_data):
        pass

    def __handle_request_block(self, block_id):
        block = self.get_block_callback(block_id)
        if block is None:
            return None
        return block.to_dict()

    def __handle_request_transaction(self, transaction_hash):
        pass


ClientNetworkInterface = NetworkInterface
