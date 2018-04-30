"""
Test Plan
=========

Peer List Exchange: Server
-------------------------

#1

Given

- Node peer list is {"192.168.2.3": {"port": 6666}}

When

- Node gets RPC request { "jsonrpc": "2.0", method: "getPeers", params:[], id: 1}

Then

- Node returns { "jsonrpc": "2.0", result: {"192.168.2.3": {"port": 6666}}, id: 1}

#1a

Given

-  Node peer list is {}

When

- Node gets RPC request { "jsonrpc": "2.0", method: "getPeers", params:[], id: 1}

Then

- Node returns { "jsonrpc": "2.0", result: {}, id: 1}

#2

Given

- Node peer list is {}

When

- Node gets RPC request { "jsonrpc": "2.0", method: "advertisePeer", params:[6667], id: 1}

Then

- Node returns { "jsonrpc": "2.0", result: true, id: 1}
- Node peer list is {"<ip of client>": {"port": 6667}}

#2a

Given

- Node peer list is {}

When

- Node gets RPC request { "jsonrpc": "2.0", method: "advertisePeer", params:[], id: 1}

Then

- Node returns { "jsonrpc": "2.0", result: true, id: 1}
- Node peer list is {"<ip of client>": {"port": 6666}}

Peer List Exchange: Client
--------------------------

#3

Given

- Client's peer list is empty

When

- Client runs "exchange_peer_lists" method
- Client gets { "jsonrpc": "2.0", result: {"192.168.2.3": {"port": 6666}}, id: 1}

Then

- Client sent { "jsonrpc": "2.0", method: "getPeers", params:[], id: 1}
- Clients peer list is {"192.168.2.3": {"port": 6666}}

"""
import json
from unittest import TestCase

from werkzeug.test import Client

from labchain.networking import ServerNetworkInterface


class MockJsonRpcClient:
    """"""

    def __init__(self):
        self.requests = {}
        self.response_queue = []

    def queue_response(self, response_dict):
        self.response_queue.append(response_dict)

    def send(self, ip_address, port, data):
        key = str(ip_address) + str(port)
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append(data)
        return json.dumps(self.response_queue.pop())


class CommonTestCase(TestCase):

    def create_server_network_interface(self, json_rpc_client):
        return ServerNetworkInterface(json_rpc_client, {}, self.on_block_received,
                                      self.on_transaction_received, self.get_block, self.get_transaction)

    def setUp(self):
        # key block ID -> value block instance
        self.available_blocks = {}
        # key transaction hash -> value transaction instance
        self.available_transactions = {}
        self.received_blocks = []
        self.received_transactions = []
        self.server_json_rpc_client = MockJsonRpcClient()
        self.server_network_interface = self.create_server_network_interface(self.server_json_rpc_client)
        self.client = Client(self.server_network_interface.werkzeug_app)

    def on_block_received(self, block):
        self.received_blocks.append(block)

    def on_transaction_received(self, transaction):
        self.received_transactions.append(transaction)

    def get_block(self, block_id):
        if block_id in self.available_blocks:
            return self.available_blocks[block_id]
        return None

    def get_transaction(self, transaction_hash):
        if transaction_hash in self.available_transactions:
            return self.available_transactions[transaction_hash]
        return None

    def get_peer_list(self):
        return self.server_network_interface.peers

    def add_peer(self, host, port=6666):
        self.server_network_interface.peers[host] = {'port': port}

    def make_request(self, data):
        """Make a request to the node and return the response dict."""
        app_iter, status, headers = self.client.post('/', data=json.dumps(data))
        return ''.join(app_iter)


class PeerListExchangeTestCase(CommonTestCase):
    def test_get_peers_with_one_entry(self):
        """Test case #1."""
        # given
        self.add_peer('192.168.2.3', 6666)
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", method: "getPeers", params:[], id: 1}')
        # then
        self.assertEqual(response_data, '{ "jsonrpc": "2.0", result: {"192.168.2.3": {"port": 6666}}, id: 1}')
