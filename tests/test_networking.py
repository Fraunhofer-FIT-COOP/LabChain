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

    def queue_response(self, response_data):
        """Set the content of the result field for future requests."""
        self.response_queue.append(response_data)

    def send(self, ip_address, port, method, params=[]):
        """Store a json RPC call in self.requests."""
        key = str(ip_address) + ':' + str(port)
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append((method, params))
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
        self.json_rpc_client = MockJsonRpcClient()
        self.network_interface = self.create_server_network_interface(self.json_rpc_client)
        self.client = Client(self.network_interface.werkzeug_app)

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
        return self.network_interface.peers

    def add_peer(self, host, port=6666):
        self.network_interface.peers[host] = {'port': port}

    def make_request(self, data):
        """Make a request to the node and return the response dict."""
        app_iter, status, headers = self.client.post('/', data=json.dumps(data))
        return ''.join(app_iter)

    def get_last_request(self, host, port):
        key = str(host) + ':' + str(port)
        if key not in self.json_rpc_client.requests or len(self.json_rpc_client.requests[key]) == 0:
            return None, None
        return self.json_rpc_client.requests[key][-1]

    def assert_json_equal(self, json_expected, json_actual):
        """Assert that two JSON strings contain the same data."""
        self.assertEqual(json.loads(json_expected), json.loads(json_actual))


class PeerListExchangeTestCase(CommonTestCase):
    def test_get_peers_with_one_entry(self):
        """Test case #1."""
        # given
        self.add_peer('192.168.2.3', 6666)
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", method: "getPeers", params:[], id: 1}')
        # then
        self.assert_json_equal(response_data, '{ "jsonrpc": "2.0", result: {"192.168.2.3": {"port": 6666}}, id: 1}')


class SendTransactionTestCase(CommonTestCase):

    def test_send_transaction_server_valid(self):
        """Test Case #5"""

        # Given
        self.add_peer('192.168.2.3', 6666)

        # When
        # Server gets request from Client
        response = self.make_request('{ "jsonrpc": "2.0", method: "sendTransaction", '
                                     'params:  [{"sender": "test_sender", "receiver": "test_receiver", '
                                     '"payload": "test_payload", "signature": "test_signature"}], id: 1}')
        # Then
        # assert transaction
        transaction = self.received_transactions[0]
        self.assertEqual(transaction.sender, 'test_sender')
        self.assertEqual(transaction.receiver, 'test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

        # assert response
        self.assert_json_equal(response, '{"jsonrpc": "2.0", result: true, id: 1}')

    def test_send_transaction_client_valid(self):
        """Test Case #6"""
        # Given
        self.add_peer('192.168.2.3', 6666)

        # TODO A transaction with sender "test_sender",
        # receiver "test_receiver",
        # payload "test_payload" and
        # signature "test_signature"
        test_transaction = None

        # When
        self.json_rpc_client.queue_response({
            'jsonrpc': '2.0',
            'result': True,
            'id': 1
        })
        self.network_interface.sendTransaction(test_transaction)

        # Then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'sendTransaction')
        self.assertEqual(last_request_params, [{'sender': 'test_sender',
                                                'receiver': 'test_receiver',
                                                'payload': 'test_payload',
                                                'signature': 'test_signature'}])


class SendBlockTestCase(CommonTestCase):

    def test_send_block_server_valid(self):
        """Test Case #7"""
        # Given
        self.add_peer('192.168.2.3', 6666)

        # When
        # Server gets request from Client
        response = self.make_request('{ "jsonrpc": "2.0", method: "sendBlock", '
                                     'params:  [{"nr" : 2,"merkleHash" : "merkel_hash123", '
                                     '"predecessorBlock" : "pre_hash123","nonce" : 6969,"creator" : "test_creator", '
                                     '"transactions" : [{"sender": "test_sender", "receiver": "test_receiver", '
                                     '"payload": "test_payload", "signature": "test_signature"}], id: 1}')

        # Then
        block = self.received_blocks[0]
        self.assertEqual(block.merkle_tree_root, 'merkle_hash123')
        self.assertEqual(block.predecessor_hash, 'pre_hash123')
        self.assertEqual(block.nonce, 6969)
        self.assertEqual(block.block_creator_id, 'test_creator')
        self.assertEqual(len(block.transactions), 1)
        transaction = block.transactions[0]
        self.assertEqual(transaction.sender, 'test_sender')
        self.assertEqual(transaction.receiver, 'test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

        # assert response
        self.assert_json_equal(response, '{"jsonrpc": "2.0", result: true, id: 1}')

    def test_send_block_client_valid(self):
        """Test Case #8"""
        # Given
        self.add_peer('192.168.2.3', 6666)

        # TODO Send a block with params:
        # "nr" : 2,
        # "merkleHash" : "merkel_hash123",
        # "predecessorBlock" : "pre_hash123",
        # "nonce" : 6969,
        # "creator" : "test_creator",
        # "transactions" : [{"sender": "test_sender", "receiver": "test_receiver", "payload": "test_payload",
        # "signature": "test_signature"

        test_block = None

        self.json_rpc_client.queue_response({
            'jsonrpc': '2.0',
            'result': True,
            'id': 1
        })
        self.network_interface.sendBlock(test_block)

        # Then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'sendBlock')
        self.assertEqual(last_request_params, [{'nr': 2, 'merkleHash': 'merkle_hash123',
                                                'predecessorBlock': 'pre_hash123', 'nonce': 6969,
                                                'creator': 'test_creator',
                                                'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver',
                                                                  'payload': 'test_payload',
                                                                  'signature': 'test_signature'}]}])


class RequestBlockClientTestCase(CommonTestCase):
    def test_request_block(self):
        """Test case #16."""
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response({
            'nr': 2,
            'merkleHash': 'test_merkle_hash',
            'predecessorBlock': None,
            'nonce': 5,
            'creator': 'test_creator',
            'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver', 'payload': 'test_payload',
                              'signature': 'test_signature'}]})
        block = self.network_interface.requestBlock(2)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlock')
        self.assertEqual(last_request_params, [])
        self.assertEqual(block.merkle_tree_root, 'test_merkle_hash')
        self.assertEqual(block.predecessor_hash, None)
        self.assertEqual(block.nonce, 5)
        self.assertEqual(block.block_creator_id, 'test_creator')
        self.assertEqual(len(block.transactions), 1)
        transaction = block.transactions[0]
        self.assertEqual(transaction.sender, 'test_sender')
        self.assertEqual(transaction.receiver, 'test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

    def test_request_nonexistent_block(self):
        """Test case #17."""
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response(None)
        block = self.network_interface.requestBlock(2)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlock')
        self.assertIsNone(block)


class RequestTransactionServerTestCase(CommonTestCase):
    def test_request_transaction(self):
        """test case #9 """
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = {"sender": "test_sender", "receiver": "test_receiver",
                                                                 "payload": "test_payload",
                                                                 "signature": "test_signature"}
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestTransaction", "params": ["hash_of_transaction_#1"],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))

        # then
        self.assert_json_equal(response,
                               '{ "jsonrpc": "2.0", result: {"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"},id: 1}')

    def test_request_nonexistent_transaction(self):
        """test case #10 """
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestTransaction", "params": ["hash_of_transaction_#1"],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))
        # then
        self.assert_json_equal(response, '{ "jsonrpc": "2.0", result: null, id: 1}')


class RequestTransactionClientTestCase(CommonTestCase):
    def test_request_transaction(self):
        """test case #11 """
        # given
        self.add_peer('192.168.100.4', 6666)

        self.json_rpc_client.queue_response({
            'sender': 'pubkey_of_test_sender',
            'receiver': 'pubkey_of_test_receiver',
            'payload': 'test_payload',
            'signature': 'test_signature'})
        transaction = self.network_interface.requestTransaction('hash_of_transaction_#1')

        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')
        self.assertEqual(last_request_params, [])

        self.assertEqual(transaction.sender, 'pubkey_of_test_sender')
        self.assertEqual(transaction.receiver, 'pubkey_of_test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

    def test_request_nonexistent_transaction(self):
        """test case #12 """
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response(None)
        transaction = self.network_interface.requestTransaction('non_existent_hash')
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')
        self.assertIsNone(transaction)
