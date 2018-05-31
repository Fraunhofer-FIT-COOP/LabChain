import argparse
import logging
import os
import sys

# append project dir to python path
from labchain.cryptoHelper import CryptoHelper
from labchain.networking import ClientNetworkInterface, JsonRpcClient

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

from labchain.client import Wallet, BlockchainClient  # noqa

CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
WALLET_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'wallet.csv')


def create_config_directory():
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)


def create_client(wallet_file, node_ip, node_port):
    crypto_helper = CryptoHelper.instance()
    network_interface = ClientNetworkInterface(JsonRpcClient(), {node_ip: {node_port: {}}})
    return BlockchainClient(Wallet(wallet_file), network_interface, crypto_helper)


def setup_logging(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser(description='CLI client for Labchain.')
    parser.add_argument('node_ip', help='The IP address of the Labchain node')
    parser.add_argument('node_port', help='The port address of the Labchain node')
    parser.add_argument('--verbose', '-v', action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.verbose)
    create_config_directory()
    if os.path.exists(WALLET_FILE_PATH):
        file_mode = 'r+'
    else:
        file_mode = 'w+'
    with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
        client = create_client(open_wallet_file, args.node_ip, args.node_port)
        client.main()
