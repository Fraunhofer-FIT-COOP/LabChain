import json
import random
import time
import collections

import requests
from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from labchain.block import Block
from labchain.transaction import Transaction


class NodeNotAvailableException(Exception):
    pass


class NodeTimeoutException(Exception):
    pass


class TransactionDoesNotExistException(Exception):
    pass


class BlockDoesNotExistException(Exception):
    pass


def update(d, u):
    """Recursive dictionary update"""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


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
        # send the transaction to all peers
        for ip, port_dict in self.peers.items():
            for port in port_dict.items():
                self.json_rpc_client.send(ip, port[0], 'sendTransaction', [transaction.to_dict()])

    def sendBlock(self, block):
        # send the block to all peers
        for ip, port_dict in self.peers.items():
            for port in port_dict.items():
                self.json_rpc_client.send(ip, port[0], 'sendBlock', [block.to_dict()])

    def requestTransaction(self, transaction_hash):
        shuffled_peer_ips = self.__get_shuffled_peers()
        for peer_ip in shuffled_peer_ips:
            for peer_port in self.peers[peer_ip]:
                transaction = self.json_rpc_client.send(peer_ip, peer_port, 'requestTransaction', [transaction_hash])
                if transaction:
                    return Transaction.from_dict(transaction)
        return None

    def requestBlock(self, block_id):
        """Request a single block by block ID."""
        shuffled_peer_ips = self.__get_shuffled_peers()
        for peer_ip in shuffled_peer_ips:
            for peer_port in self.peers[peer_ip]:
                block_data = self.json_rpc_client.send(peer_ip, peer_port, 'requestBlock', [block_id])
                if block_data:
                    return Block.from_dict(block_data)
        return None

    def add_peer(self, ip_address, port, info={}):
        """Add a single peer to the peer list."""
        update(self.peers, {ip_address: {port: info}})

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
            for port in self.peers[peer]:
                response = self.json_rpc_client.send(peer, port, 'getPeers')
                update(new_peers, response)
        self.peers = update(self.peers, new_peers)

    def advertise_to_peers(self):
        for peer in self.peers:
            for port in self.peers[peer]:
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
        self.on_block_received_callback(block_data)
        # TODO
        # check if block is already part of the chain or
        # was already received. Then decide to resend block to other nodes

    def __handle_send_transaction(self, transaction_data):
        self.on_transaction_received_callback(transaction_data)
        # TODO
        # check if transaction is already in a block? or still in the Tx pool?
        # Then decide to resend Tx to other nodes

    def __handle_request_block(self, block_id):
        block = self.get_block_callback(block_id)
        if block is None:
            return None
        return block.to_dict()

    def __handle_request_transaction(self, transaction_hash):
        transaction = self.get_transaction_callback(transaction_hash)
        if transaction:
            return transaction
        return None


ClientNetworkInterface = NetworkInterface
