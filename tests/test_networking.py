"""Test cases for the networking component."""
import json
import time
from unittest import TestCase

from werkzeug.test import Client

from labchain.block import Block
from labchain.networking import ServerNetworkInterface, TransactionDoesNotExistException, BlockDoesNotExistException
from labchain.transaction import Transaction


class MockJsonRpcClient:
    """"""

    def __init__(self):
        self.requests = {}
        self.response_queue = []

    def queue_response(self, response_data):
        """Set the content of the result field for future requests."""
        self.response_queue.append(response_data)

    def send(self, ip_address, port, method, params=tuple()):
        """Store a json RPC call in self.requests."""
        key = str(ip_address) + ':' + str(port)
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append((method, params))
        response = self.response_queue.pop()
        return response['result']


class MockCryptoHelper:
    def __init__(self):
        self.key_counter = 1
        self.hash_counter = 1
        self.hash_map = {}

    def hash(self, message):
        if message not in self.hash_map:
            self.hash_map[message] = '{num:05d}'.format(num=self.hash_counter)
            self.hash_counter += 1
        return self.hash_map[message]


class CommonTestCase(TestCase):

    def create_server_network_interface(self, json_rpc_client):
        return ServerNetworkInterface(json_rpc_client, {}, MockCryptoHelper(), self.on_block_received,
                                      self.on_transaction_received, self.get_block, self.get_transaction, port=6666)

    def setUp(self):
        # key block ID -> value block instance
        self.available_blocks = {}
        # key transaction hash -> value transaction instance
        self.available_transactions = {}
        self.received_blocks = []
        self.received_transactions = []
        self.json_rpc_client = MockJsonRpcClient()
        self.network_interface = self.create_server_network_interface(self.json_rpc_client)
        self.client = Client(self.network_interface.application)

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

    def add_peer(self, host, port=6666, info=None):
        if info is None:
            info = {}
        self.network_interface.peers[host] = {port: info}

    def make_request(self, data):
        """Make a request to the node and return the response dict."""
        app_iter, status, headers = self.client.post('/', data=data,
                                                     environ_base={'REMOTE_ADDR': '1.2.3.4'},
                                                     headers={'Content-Type': 'application/json'})
        result = ''
        for line in app_iter:
            result += line.decode()
        return result

    def get_last_request(self, host, port):
        key = str(host) + ':' + str(port)
        if key not in self.json_rpc_client.requests or len(self.json_rpc_client.requests[key]) == 0:
            return None, None
        return self.json_rpc_client.requests[key][-1]

    def assert_json_equal(self, json_expected, json_actual):
        """Assert that two JSON strings contain the same data."""
        self.assertEqual(json.loads(json_expected), json.loads(json_actual))


class PeerListExchangeTestCase(CommonTestCase):

    def test_server_test_get_peers_with_one_entry(self):
        """Test case #1."""
        # given
        self.add_peer('192.168.2.3', 6666)
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", "method": "getPeers", "params":[], "id": 1}')
        # then
        self.assert_json_equal(response_data, '{ "jsonrpc": "2.0", "result": {"192.168.2.3": {"6666": {}}}, "id": 1}')

    def test_server_test_get_peers_with_no_entries(self):
        """Test case #1a."""
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", "method": "getPeers", "params":[], "id": 1}')
        # then
        self.assert_json_equal(response_data, '{ "jsonrpc": "2.0", "result": {}, "id": 1}')

    def test_server_advertise_peer_with_port_param(self):
        """Test case #2."""
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", "method": "advertisePeer", "params":[6667], "id": 1}')
        # then
        self.assert_json_equal(response_data, '{ "jsonrpc": "2.0", "result": true, "id": 1}')
        self.assertDictEqual(self.network_interface.peers, {"1.2.3.4": {6667: {}}})

    def test_server_advertise_peer_with_no_port_param(self):
        """Test case #2a."""
        # when
        response_data = self.make_request('{ "jsonrpc": "2.0", "method": "advertisePeer", "id": 1}')
        # then
        self.assert_json_equal(response_data, '{ "jsonrpc": "2.0", "result": true, "id": 1}')
        self.assertDictEqual(self.network_interface.peers, {"1.2.3.4": {6666: {}}})

    def test_client_exchange_peer_list(self):
        """Test case #3."""
        # given
        self.add_peer('192.168.121.77', 6666)
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': {'192.168.2.3': {6666: {}}}, 'id': 1})
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': {'192.168.5.6': {6666: {}}}, 'id': 1})
        self.network_interface.update_peer_lists()
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.121.77', 6666)
        self.assertEqual(last_request_method, 'getPeers')
        self.assertFalse(last_request_params)
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'getPeers')
        self.assertFalse(last_request_params, [])
        self.assertDictEqual(self.network_interface.peers,
                             {'192.168.2.3': {6666: {}}, '192.168.5.6': {6666: {}},
                              '192.168.121.77': {6666: {}}, '192.168.100.4': {6666: {}}})

    def test_client_advertise_peer(self):
        """Test case #4."""
        # given
        self.add_peer('192.168.121.77', 6666)
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': True, 'id': 1})
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': True, 'id': 1})
        self.network_interface.advertise_to_peers()
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.121.77', 6666)
        self.assertEqual(last_request_method, 'advertisePeer')
        self.assertEqual([6666], last_request_params)
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'advertisePeer')
        self.assertEqual([6666], last_request_params)


class SendTransactionTestCase(CommonTestCase):

    def test_send_transaction_server_valid(self):
        """Test Case #5"""
        # When
        # Server gets request from Client
        response = self.make_request('{"jsonrpc": "2.0", "method": "sendTransaction", '
                                     '"params":  [{"sender": "test_sender", "receiver": "test_receiver", '
                                     '"payload": "test_payload", "signature": "test_signature"}], "id": 1}')
        # Then
        # assert transaction
        transaction = self.received_transactions[0]
        self.assertEqual(transaction.sender, 'test_sender')
        self.assertEqual(transaction.receiver, 'test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

        # assert response
        self.assert_json_equal(response, '{"jsonrpc": "2.0", "result": null, "id": 1}')

    def test_send_transaction_client_valid(self):
        """Test Case #6"""
        # given
        self.add_peer('192.168.2.3', 6666)

        test_transaction = Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        # when
        self.json_rpc_client.queue_response({
            'jsonrpc': '2.0',
            'result': True,
            'id': 1
        })
        self.network_interface.sendTransaction(test_transaction)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.2.3', 6666)
        self.assertEqual(last_request_method, 'sendTransaction')
        self.assertEqual(last_request_params, [{"sender": "test_sender", "receiver": "test_receiver",
                                                "payload": "test_payload", "signature": "test_signature"}])


class SendBlockTestCase(CommonTestCase):

    def test_send_block_server_valid(self):
        """Test Case #7"""
        # When
        # Server gets request from Client
        response = self.make_request('{"jsonrpc": "2.0", "method": "sendBlock", '
                                     '"params":  [{'
                                     '"nr" : 2, "merkleHash" : "merkle_hash123", '
                                     '"predecessorBlock" : "pre_hash123","nonce" : 6969, '
                                     '"creator" : "test_creator", "timestamp": 0.0 , '
                                     '"transactions" : ['
                                     '{"sender": "test_sender", "receiver": "test_receiver", '
                                     '"payload": "test_payload", "signature": "test_signature"}]}], "id": 1}')

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
        self.assert_json_equal(response, '{"jsonrpc": "2.0", "result": null, "id": 1}')

    def test_send_block_client_valid(self):
        """Test Case #8"""
        # Given
        self.add_peer('192.168.100.4', 6666)
        now = time.time()
        test_block = Block(2, 'merkle_hash123', 'pre_hash123', 'test_creator',
                           [Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')],
                           6969, now)
        # when
        self.json_rpc_client.queue_response({
            'jsonrpc': '2.0',
            'result': None,
            'id': 1
        })
        self.network_interface.sendBlock(test_block)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'sendBlock')
        self.assertEqual(last_request_params, [{'nr': 2, 'timestamp': now, 'merkleHash': 'merkle_hash123',
                                                'predecessorBlock': 'pre_hash123', 'nonce': 6969,
                                                'creator': 'test_creator',
                                                'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver',
                                                                  'payload': 'test_payload',
                                                                  'signature': 'test_signature'}]}])


class RequestTransactionServerTestCase(CommonTestCase):
    def test_request_transaction(self):
        """test case #9 """
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestTransaction", "params": ["hash_of_transaction_#1"],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))

        # then
        self.assert_json_equal(response,
                               '{"result": {"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}, "id": 1,"jsonrpc": "2.0"}')

    def test_request_nonexistent_transaction(self):
        """test case #10 """
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestTransaction", "params": ["hash_of_transaction_#1"],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))
        # then
        self.assert_json_equal(response, '{ "jsonrpc": "2.0", "result": null, "id": 1}')


class RequestTransactionClientTestCase(CommonTestCase):
    def test_request_transaction(self):
        """test case #11 """
        # given
        self.add_peer('192.168.100.4', 6666)

        self.json_rpc_client.queue_response({'jsonrpc': '2.0',
                                             'result': {
                                                 'sender': 'pubkey_of_test_sender',
                                                 'receiver': 'pubkey_of_test_receiver',
                                                 'payload': 'test_payload',
                                                 'signature': 'test_signature'},
                                             'id': 1})
        transaction = self.network_interface.requestTransaction('hash_of_transaction_#1')

        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')
        self.assertEqual(last_request_params, ['hash_of_transaction_#1'])
        self.assertEqual(transaction.sender, 'pubkey_of_test_sender')
        self.assertEqual(transaction.receiver, 'pubkey_of_test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

    def test_request_nonexistent_transaction(self):
        """test case #12 """
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': None, 'id': 1})
        with self.assertRaises(TransactionDoesNotExistException):
            self.network_interface.requestTransaction('non_existent_hash')
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')


class RequestBlockServerTestCase(CommonTestCase):
    def test_request_block(self):
        """Test case #13."""
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', 'test_pred_block_hash', 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestBlock", "params": [2],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))
        # then
        self.assert_json_equal(response, '{ "jsonrpc": "2.0", "result": {"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"predecessorBlock" : "test_pred_block_hash", "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}, "id":1}'
                               )

    def test_request_block_with_no_predecessor(self):
        """Test case #14."""
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', None, 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestBlock", "params": [2],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))
        # then
        self.assert_json_equal(response, '{ "jsonrpc": "2.0", "result": {"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"predecessorBlock" : null, "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}, "id":1}'
                               )

    def request_nonexisting_block(self):
        """Test case #15."""
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "requestBlock", "params": [2],
                            "id": 1}
        response = self.make_request(json.dumps(json_rpc_request))
        # then
        self.assert_json_equal(response, '{"jsonrpc": "2.0", "result": null, id: 1}')


class RequestBlockClientTestCase(CommonTestCase):
    def test_request_block(self):
        """Test case #16."""
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_response({
            'jsonrpc': '2.0',
            'result': {
                'nr': 2,
                'merkleHash': 'test_merkle_hash',
                'predecessorBlock': None,
                'nonce': 5,
                'creator': 'test_creator',
                'timestamp': 1337.0,
                'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver', 'payload': 'test_payload',
                                  'signature': 'test_signature'}]},
            'id': 1
        })
        block = self.network_interface.requestBlock(2)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlock')
        self.assertEqual(last_request_params, [2])
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
        self.json_rpc_client.queue_response({'jsonrpc': '2.0', 'result': None, 'id': 1})
        with self.assertRaises(BlockDoesNotExistException):
            self.network_interface.requestBlock(2)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlock')
