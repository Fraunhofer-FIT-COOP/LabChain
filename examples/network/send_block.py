import hashlib
import logging
import os
import sys
import time
from threading import Thread

# append project dir to python path
from labchain import networking
from labchain.block import Block
from labchain.transaction import Transaction
from tests.test_account import MockCryptoHelper

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from labchain.networking import ServerNetworkInterface, JsonRpcClient, TransactionDoesNotExistException  # noqa

# change to DEBUG to see more output
LOG_LEVEL = logging.INFO
# change the polling interval
POLL_INTERVAL = 10

BLOCK = Block(1, 'some_root', 'pred_hash', 'creator_id',
              [Transaction('some sender', 'some_receiver', 'some_payload', 'some_signature')],
              1234)
RECEIVED_BLOCKS = {}


def get_block(block_id):
    if block_id in RECEIVED_BLOCKS:
        return RECEIVED_BLOCKS[block_id]
    return None


def on_block_received(received_block):
    RECEIVED_BLOCKS[received_block.block_number] = received_block
    logging.warning('Received block: {}'.format(received_block))


def empty_function():
    """Empty function for unneeded functionality."""
    pass


def create_network_interface(port, initial_peers=None):
    if initial_peers is None:
        initial_peers = {}
    return ServerNetworkInterface(JsonRpcClient(), initial_peers, MockCryptoHelper(), on_block_received,
                                  empty_function, get_block, empty_function, port)


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
        transaction = interface2.sendBlock(BLOCK)
        time.sleep(POLL_INTERVAL)
