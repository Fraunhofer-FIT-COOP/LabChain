import logging
import os
import sys
from threading import Thread

# append project dir to python path
from labchain.network import networking
from tests.test_account import MockCryptoHelper
from labchain.network.networking import ServerNetworkInterface, JsonRpcClient

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if project_dir not in sys.path:
    sys.path.append(project_dir)

# change to DEBUG to see more output
LOG_LEVEL = logging.INFO
# change the polling interval
POLL_INTERVAL = 10


def empty_function():
    """Empty function for unneeded functionality."""
    pass


def create_network_interface(port, initial_peers=None):
    if initial_peers is None:
        initial_peers = {}
    return ServerNetworkInterface(json_rpc_client = JsonRpcClient(),
                                    initial_peers = initial_peers,
                                    crypto_helper = MockCryptoHelper(),
                                    on_block_received_callback = empty_function,
                                    on_transaction_received_callback = empty_function,
                                    get_block_callback = empty_function,
                                    get_block_by_hash_callback = empty_function,
                                    get_transaction_callback = empty_function,
                                    get_contract_callback = empty_function,
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
    webserver_thread2 = Thread(name='Web Server #2', target=interface2.start_listening, args=(False,))
    webserver_thread1.start()
    webserver_thread2.start()
    logging.debug('Done')

    # start the polling threads
    logging.debug('Starting polling threads...')
    polling_thread1 = Thread(name='Polling #1', target=interface1.poll_update_peer_lists, args=(POLL_INTERVAL,))
    polling_thread2 = Thread(name='Polling #2', target=interface2.poll_update_peer_lists, args=(POLL_INTERVAL,))
    polling_thread1.start()
    polling_thread2.start()
    logging.debug('Done')
