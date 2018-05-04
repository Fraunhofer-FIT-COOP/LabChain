import json
import random

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
        shuffled_peer_ips = self.__get_shuffeled_peers()
        for peer_ip in shuffled_peer_ips:
            peer_port = self.peers[peer_ip]['port']
            block_data = self.json_rpc_client.send(peer_ip, peer_port, 'requestBlock', [block_id])
            if block_data:
                return Block.from_dict(block_data)
        return None

    def add_peer(self, ip_address, port):
        self.peers.append({ip_address: {'port': port}})

    def __get_shuffeled_peers(self):
        """Retrieve a shuffled list of peer IP addresses."""
        peer_ips = self.peers.keys()
        random.shuffle(peer_ips)
        return peer_ips


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
        self.get_block_callback = get_block_callback
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

        # insert IP address of peer if advertise peer is called
        request_body_dict = json.loads(request.data.decode())
        if request_body_dict['method'] == 'advertisePeer':
            request_body_dict['params'].insert(0, request.remote_addr)
        request.data = json.dumps(request_body_dict)

        response = JSONRPCResponseManager.handle(
            request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    def __handle_get_peers(self):
        return {}

    def __handle_advertise_peer(self, remote_address, port):
        pass

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
