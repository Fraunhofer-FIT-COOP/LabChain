import logging
import os
import sys
import time
from threading import Thread

# append project dir to python path
from labchain.network import networking
from labchain.datastructure.block import Block
from labchain.datastructure.transaction import Transaction
from tests.test_account import MockCryptoHelper
from labchain.network.networking import ServerNetworkInterface, JsonRpcClient

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if project_dir not in sys.path:
    sys.path.append(project_dir)


# change to DEBUG to see more output
LOG_LEVEL = logging.INFO
# change the polling interval
POLL_INTERVAL = 10

BLOCK = Block(1, 'some_root', 'pred_hash', 'creator_id',
              [Transaction('some sender', 'some_receiver', 'some_payload', 'some_type', 'some_signature')],
              1234)
RECEIVED_BLOCKS = {}


def get_block(block_id):
    if block_id in RECEIVED_BLOCKS:
        return [RECEIVED_BLOCKS[block_id]]
    return []


def on_block_received(received_block):
    RECEIVED_BLOCKS[received_block.block_id] = received_block
    logging.warning('Received block: {}'.format(received_block))


def empty_function():
    """Empty function for unneeded functionality."""
    pass


def create_network_interface(port, initial_peers=None):
    if initial_peers is None:
        initial_peers = {}
    return ServerNetworkInterface(json_rpc_client = JsonRpcClient(),
                                    initial_peers = initial_peers,
                                    crypto_helper = MockCryptoHelper(),
                                    on_block_received_callback = on_block_received,
                                    on_transaction_received_callback = empty_function,
                                    get_block_callback = get_block,
                                    get_block_by_hash_callback = empty_function,
                                    get_transaction_callback = empty_function,
                                    get_contract_callback = empty_function,
                                    get_contract_state_callback = empty_function,
                                    get_methods_callback = empty_function,
                                    get_blocks_by_hash_range = empty_function,
                                    port= port)


def configure_logging():
    logging.basicConfig(level=logging.WARNING, format='%(threadName)s: %(message)s')
    logging.getLogger(networking.__name__).setLevel(LOG_LEVEL)


if __name__ == '__main__':
    configure_logging()

    # two interfaces: one without peers and one with the other as peer
    interface1 = create_network_interface(8080)
    interface2 = create_network_interface(8081, initial_peers={'127.0.0.1': {8080: {}}})

    # start the web servers for receiving JSON-RPC calls
    logging.debug('Starting web server threads...')
    webserver_thread1 = Thread(name='Web Server #1', target=interface1.start_listening, args=(False,))
    webserver_thread1.start()
    logging.debug('Done')

    while True:
        logging.warning('Sending block: {}'.format(str(BLOCK)))
        interface2.sendBlock(BLOCK)
        time.sleep(POLL_INTERVAL)
