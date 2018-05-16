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

from labchain.networking import ServerNetworkInterface, JsonRpcClient, TransactionDoesNotExistException, \
    BlockDoesNotExistException  # noqa

# change to DEBUG to see more output
LOG_LEVEL = logging.INFO
# change the polling interval
POLL_INTERVAL = 10

BLOCKS = {1: Block(1, 'some_root', 'pred_hash', 'creator_id',
                   [Transaction('some sender', 'some_receiver', 'some_payload', 'some_signature')],
                   1234)}


def get_block(block_id):
    if int(block_id) in BLOCKS:
        return BLOCKS[block_id]
    return None


def empty_function():
    """Empty function for unneeded functionality."""
    pass


def create_network_interface(port, initial_peers=None):
    if initial_peers is None:
        initial_peers = {}
    return ServerNetworkInterface(JsonRpcClient(), initial_peers, MockCryptoHelper(), empty_function, empty_function,
                                  get_block, empty_function, port)


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
        logging.warning('Requesting block 1')
        block = interface2.requestBlock(1)
        logging.warning('Received block: {}'.format(str(block)))

        logging.warning('Requesting block 2')
        try:
            block = interface2.requestBlock(2)
            logging.error('This statement should not be reached')
        except BlockDoesNotExistException:
            logging.warning('Block does not exist')
        time.sleep(POLL_INTERVAL)
