import os
import sys

# append project dir to python path
from labchain.cryptoHelper import CryptoHelper

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

from labchain.client import Wallet, BlockchainClient  # noqa
from tests.test_account import MockNetworkInterface  # noqa

CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
WALLET_FILE_PATH = os.path.join(CONFIG_DIRECTORY, 'wallet.csv')


def create_config_directory():
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)


def create_client(wallet_file):
    crypto_helper = CryptoHelper.instance()
    network_interface = MockNetworkInterface(crypto_helper, [], [])
    return BlockchainClient(Wallet(wallet_file), network_interface, crypto_helper)


if __name__ == '__main__':
    create_config_directory()
    if os.path.exists(WALLET_FILE_PATH):
        file_mode = 'r+'
    else:
        file_mode = 'w+'
    with open(WALLET_FILE_PATH, file_mode) as open_wallet_file:
        client = create_client(open_wallet_file)
        client.main()
