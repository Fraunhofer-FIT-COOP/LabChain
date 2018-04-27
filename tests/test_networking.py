"""
#1





"""
import json
from threading import Thread
from unittest import TestCase

from labchain.networking import ServerNetworkInterface

TEST_SERVER_PORT = 6666


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

    def run_server(self, network_interface, port):
        self.server_thread = Thread(target=network_interface.start_listening, args=[port])
        self.server_thread.daemon = True
        self.server_thread.start()

    def create_server_network_interface(self, json_rpc_client):
        return ServerNetworkInterface(json_rpc_client, [], self.on_block_received,
                                      self.on_transaction_received)

    def setUp(self):
        self.received_blocks = []
        self.received_transactions = []
        if not self.server_thread:
            self.server_json_rpc_client = MockJsonRpcClient()
            self.server_network_interface = self.create_server_network_interface(self.server_json_rpc_client)
            self.run_server(self.server_network_interface, TEST_SERVER_PORT)

    def on_block_received(self, block):
        self.received_blocks.append(block)

    def on_transaction_received(self, transaction):
        self.received_transactions.append(transaction)
