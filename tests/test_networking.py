"""Test cases for the networking component."""
import json
import time
from unittest import TestCase

from werkzeug.test import Client

from labchain.datastructure.block import Block
from labchain.network.networking import ServerNetworkInterface, TransactionDoesNotExistException, BlockDoesNotExistException
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper


class MockJsonRpcClient:

    def __init__(self):
        self.requests = {}
        self.response_queue = []

    def queue_result(self, result):
        """Set the content of the result field for future requests."""
        self.response_queue.append( {'jsonrpc': '2.0', 'result': result, 'id': 1})

    def send(self, ip_address, port, method, params=tuple()):
        """Store a json RPC call in self.requests."""
        key = str(ip_address) + ':' + str(port)
        if key not in self.requests:
            self.requests[key] = []
        self.requests[key].append((method, params))
        response = self.response_queue.pop()
        return response['result']

class CommonTestCase(TestCase):

    def create_server_network_interface(self, json_rpc_client):
        return ServerNetworkInterface(
                                        json_rpc_client,
                                        {}, 
                                        CryptoHelper.instance(), 
                                        self.on_block_received,
                                        self.on_transaction_received, 
                                        self.get_block, 
                                        self.get_block_by_hash,
                                        self.get_transaction, 
                                        self.get_blocks_by_hash_range,
                                        self.empty_function,
                                        self.get_transactions_in_pool,
                                        self.get_n_last_transactions,
                                        False,
                                        port=6666)

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
            return [self.available_blocks[block_id]]
        return []

    def get_blocks_by_hash_range(self, start_hash=None, end_hash=None):
        return [block for block in self.available_blocks.values()]

    def get_block_by_hash(self, block_hash):
        for block_id in self.available_blocks:
            if self.available_blocks[block_id].merkle_tree_root == block_hash:
                return self.available_blocks[block_id]
        return None

    def get_transaction(self, transaction_hash):
        if transaction_hash in self.available_transactions:
            return self.available_transactions[transaction_hash], 'test_block_hash'
        return None, None

    def get_peer_list(self):
        return self.network_interface.peers

    def add_peer(self, host, port=6666, info=None):
        if info is None:
            info = {}
        self.network_interface.peers[host] = {port: info}

    def make_request(self, method, params=None):
        """Make a request to the node and return the response dict."""
        if params is None:
            data = '{{ "jsonrpc": "2.0", "method": "{}", "id": 1}}'.format(method)
        else:
            data = '{{ "jsonrpc": "2.0", "method": "{}", "params":{}, "id": 1}}'.format(method,params)
        app_iter, status, headers = self.client.post('/', data=data,
                                                        environ_base={'REMOTE_ADDR': '1.2.3.4'},
                                                        headers={'Content-Type': 'application/json'})
        result = ''
        for line in app_iter:
            result += line.decode()
        json_result = json.loads(result)
        return json_result["result"]

    def get_last_request(self, host, port):
        key = str(host) + ':' + str(port)
        if key not in self.json_rpc_client.requests or len(self.json_rpc_client.requests[key]) == 0:
            return None, None
        return self.json_rpc_client.requests[key][-1]

    def assert_json_equal(self, json_expected, json_actual):
        """Assert that two JSON strings contain the same data."""
        if type(json_expected) is str:
            json_expected = json.loads(json_expected)
        if type(json_actual) is str:
            json_actual = json.loads(json_actual)
        self.assertEqual(json_expected, json_actual)

    def get_n_last_transactions(self, n):
        n = int(n)
        total_transactions = []
        for transactionHash in list(self.available_transactions)[0:n]:
            total_transactions.append(self.available_transactions[transactionHash])
        return total_transactions

    def get_transactions_in_pool(self):
        return list(self.available_transactions.values())

    def empty_function():
        """Empty function for unneeded functionality."""
        pass

class PeerListExchangeTestCase(CommonTestCase):

    def test_server_test_get_peers_with_one_entry(self):
        # given
        self.add_peer('192.168.2.3', 6666)
        # when
        response_data = self.make_request("getPeers","[]")
        # then
        self.assert_json_equal(response_data, '{"192.168.2.3": {"6666": {}}}')

    def test_server_test_get_peers_with_no_entries(self):
        # when
        response_data = self.make_request("getPeers","[]")
        # then
        self.assert_json_equal(response_data, '{}')

    def test_server_advertise_peer_with_port_param(self):
        # when
        response_data = self.make_request("advertisePeer", "[6667]")
        # then
        self.assert_json_equal(response_data, 'true')
        self.assertDictEqual(self.network_interface.peers, {"1.2.3.4": {6667: {}}})

    def test_server_advertise_peer_with_no_port_param(self):
        # when
        response_data = self.make_request("advertisePeer")
        # then
        self.assert_json_equal(response_data, 'true')
        self.assertDictEqual(self.network_interface.peers, {"1.2.3.4": {6666: {}}})

    def test_client_exchange_peer_list(self):
        # given
        self.add_peer('192.168.121.77', 6666)
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result({'192.168.2.3': {6666: {}}})
        self.json_rpc_client.queue_result({'192.168.5.6': {6666: {}}})
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
        # given
        self.add_peer('192.168.121.77', 6666)
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result(True)
        self.json_rpc_client.queue_result(True)
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
        # When
        # Server gets request from Client
        response = self.make_request("sendTransaction", '[{"sender": "test_sender", "receiver": "test_receiver", "payload": "test_payload", "signature": "test_signature"}]')
        # Then
        # assert transaction
        transaction = self.received_transactions[0]
        self.assertEqual(transaction.sender, 'test_sender')
        self.assertEqual(transaction.receiver, 'test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

        # assert response
        self.assert_json_equal(response, 'null')


    def test_send_transaction_client_valid(self):
        # given
        self.add_peer('192.168.2.3', 6666)

        crypto_helper_obj = CryptoHelper.instance()
        private_key1, public_key1 = crypto_helper_obj.generate_key_pair()
        private_key2, public_key2 = crypto_helper_obj.generate_key_pair()

        test_transaction = Transaction(public_key1, public_key2, 'test_payload')
        test_transaction.sign_transaction(crypto_helper_obj, private_key1)
        # when
        self.json_rpc_client.queue_result(True)
        self.network_interface.sendTransaction(test_transaction)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.2.3', 6666)
        self.assertEqual(last_request_method, 'sendTransaction')
        self.assertEqual(last_request_params, [{"sender": public_key1, "receiver": public_key2,
                                                "payload": "test_payload", "signature": test_transaction.signature,
                                                "transaction_type": 0}])

class SendBlockTestCase(CommonTestCase):

    def test_send_block_server_valid(self):
        # When
        # Server gets request from Client
        response = self.make_request("sendBlock",'[{'
                                     '"nr" : 2, "merkleHash" : "merkle_hash123", '
                                     '"predecessorBlock" : "pre_hash123","nonce" : 6969, '
                                     '"creator" : "test_creator", "timestamp": 0.0 , "difficulty" : 0, '
                                     '"transactions" : ['
                                     '{"sender": "test_sender", "receiver": "test_receiver", '
                                     '"payload": "test_payload", "signature": "test_signature"}]}]')

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
        self.assert_json_equal(response, 'null')

    def test_send_block_client_valid(self):
        # Given
        self.add_peer('192.168.100.4', 6666)
        now = time.time()
        test_block = Block(2, 'merkle_hash123', 'pre_hash123', 'test_creator',
                           [Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')],
                           6969, now)
        # when
        self.json_rpc_client.queue_result(None)
        self.network_interface.sendBlock(test_block)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'sendBlock')
        self.assert_json_equal(last_request_params, [{'nr': 2, 'timestamp': now, 'merkleHash': 'merkle_hash123',
                                                'predecessorBlock': 'pre_hash123', 'nonce': 6969,
                                                'creator': 'test_creator',
                                                'difficulty': -1,
                                                'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver',
                                                                  'payload': 'test_payload',
                                                                  'signature': 'test_signature'}]}])

class RequestTransactionServerTestCase(CommonTestCase):
    def test_request_transaction(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        response = self.make_request("requestTransaction",'["hash_of_transaction_#1"]')

        # then
        self.assert_json_equal(response,
                               '[{"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}, "test_block_hash"]')

    def test_request_nonexistent_transaction(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        response = self.make_request("requestTransaction",'["hash_of_transaction_#1"]')
        # then
        self.assert_json_equal(response, 'null')

    def test_request_n_transaction_received(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        response = self.make_request("requestNLastTransaction",'["1"]')
        # then
        self.assert_json_equal(response,
                               '[{"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}]')

    def test_request_transaction_in_pool(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        json_rpc_request = {"jsonrpc": "2.0", "method": "", "params": [], "id": 1}
        response = self.make_request("requestTransactionsInPool",'[]')

        # then
        self.assert_json_equal(response,
                               '[{"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}]')

class RequestTransactionClientTestCase(CommonTestCase):
    def test_request_transaction(self):
        # given
        self.add_peer('192.168.100.4', 6666)

        self.json_rpc_client.queue_result([{
                                                 'sender': 'pubkey_of_test_sender',
                                                 'receiver': 'pubkey_of_test_receiver',
                                                 'payload': 'test_payload',
                                                 'signature': 'test_signature'}, 'test_block_hash'])
        transaction, block_hash = self.network_interface.requestTransaction('hash_of_transaction_#1')

        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')
        self.assertEqual(last_request_params, ['hash_of_transaction_#1'])
        self.assertEqual(transaction.sender, 'pubkey_of_test_sender')
        self.assertEqual(transaction.receiver, 'pubkey_of_test_receiver')
        self.assertEqual(transaction.payload, 'test_payload')
        self.assertEqual(transaction.signature, 'test_signature')

    def test_request_nonexistent_transaction(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result(None)
        with self.assertRaises(TransactionDoesNotExistException):
            self.network_interface.requestTransaction('non_existent_hash')
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestTransaction')

    def test_request_n_transaction_received(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        response = self.make_request("requestNLastTransaction",'["1"]')

        # then
        self.assert_json_equal(response,
                               '[{"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}]')

    def test_request_transaction_in_pool(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        self.available_transactions['hash_of_transaction_#1'] = Transaction("test_sender",
                                                                            "test_receiver",
                                                                            "test_payload",
                                                                            "test_signature")
        # when
        response = self.make_request("requestTransactionsInPool",'[]')

        # then
        self.assert_json_equal(response,
                               '[{"sender": "test_sender", "receiver": "test_receiver", '
                               '"payload": "test_payload", "signature": "test_signature"}]')

class RequestBlockServerTestCase(CommonTestCase):
    def test_request_block(self):
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', 'test_pred_block_hash', 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        response = self.make_request("requestBlock",'[2]')
        # then
        self.assert_json_equal(response, '[{"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"difficulty" : -1,'
                                         '"predecessorBlock" : "test_pred_block_hash", "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}]'
                               )

    def test_request_block_by_hash(self):
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', 'test_pred_block_hash', 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        response = self.make_request("requestBlockByHash",'["test_merkle_hash"]')
        # then
        self.assert_json_equal(response, '{"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"difficulty" : -1,'
                                         '"predecessorBlock" : "test_pred_block_hash", "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}'
                               )

    def test_request_block_with_no_predecessor(self):
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', None, 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        response = self.make_request("requestBlock",'[2]')
        # then
        self.assert_json_equal(response, '[{"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"difficulty" : -1,'
                                         '"predecessorBlock" : null, "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}]'
                               )

    def request_nonexisting_block(self):
        # when
        response = self.make_request("requestBlock",'[2]')
        # then
        self.assert_json_equal(response, 'null')

    def test_request_blocks_by_hash_range(self):
        # given
        self.available_blocks[2] = Block(2, 'test_merkle_hash', 'test_pred_block_hash', 'test_creator', [
            Transaction('test_sender', 'test_receiver', 'test_payload', 'test_signature')
        ], nonce=5, timestamp=1337.0)
        # when
        response = self.make_request("requestBlocksByHashRange",'[]')
        # then
        self.assert_json_equal(response, '[{"nr": 2, "timestamp": 1337.0, '
                                         '"merkleHash" : "test_merkle_hash", '
                                         '"difficulty" : -1,'
                                         '"predecessorBlock" : "test_pred_block_hash", "nonce" : 5, '
                                         '"creator" : "test_creator", "transactions" : '
                                         '[{"sender": "test_sender", "receiver": "test_receiver", '
                                         '"payload": "test_payload", "signature": "test_signature"}]}]'
                               )

class RequestBlockClientTestCase(CommonTestCase):
    def test_request_block(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result([
                {
                    'nr': 2,
                    'merkleHash': 'test_merkle_hash',
                    'predecessorBlock': None,
                    'nonce': 5,
                    'creator': 'test_creator',
                    'timestamp': 1337.0,
                    'difficulty': 13,
                    'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver', 'payload': 'test_payload',
                                      'signature': 'test_signature'}]
                }
            ])
        blocks = self.network_interface.requestBlock(2)
        block = blocks[0]
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

    def test_request_block_by_hash(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result(
                {
                    'nr': 2,
                    'merkleHash': 'test_merkle_hash',
                    'predecessorBlock': None,
                    'nonce': 5,
                    'creator': 'test_creator',
                    'timestamp': 1337.0,
                    'difficulty': 13,
                    'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver', 'payload': 'test_payload',
                                      'signature': 'test_signature'}]
                })
        block = self.network_interface.requestBlockByHash('test merkle_hash')
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlockByHash')
        self.assertEqual(last_request_params, ['test merkle_hash'])
        self.assertEqual(block.block_id, 2)
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
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result(None)
        with self.assertRaises(BlockDoesNotExistException):
            self.network_interface.requestBlock(2)
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlock')

    def test_request_block_by_range(self):
        # given
        self.add_peer('192.168.100.4', 6666)
        # when
        self.json_rpc_client.queue_result([
                {
                    'nr': 2,
                    'merkleHash': 'test_merkle_hash',
                    'predecessorBlock': None,
                    'nonce': 5,
                    'creator': 'test_creator',
                    'timestamp': 1337.0,
                    'difficulty': 13,
                    'transactions': [{'sender': 'test_sender', 'receiver': 'test_receiver', 'payload': 'test_payload',
                                      'signature': 'test_signature'}]
                }
            ])
        blocks = self.network_interface.requestBlocksByHashRange('test merkle_hash')
        # then
        last_request_method, last_request_params = self.get_last_request('192.168.100.4', 6666)
        self.assertEqual(last_request_method, 'requestBlocksByHashRange')
        self.assertEqual(last_request_params, ['test merkle_hash', None])
        self.assertEqual(len(blocks), 1)
        block = blocks[0]
        self.assertEqual(block.block_id, 2)
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