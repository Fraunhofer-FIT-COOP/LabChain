import os
import sys
from io import StringIO

parent_fir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if parent_fir not in sys.path:
    sys.path.append(parent_fir)

from labchain.client import Wallet, BlockchainClient
from tests.test_account import MockCryptoHelper, MockTransactionFactory, MockNetworkInterface


def create_client():
    wallet_file = StringIO()
    crypto_helper = MockCryptoHelper()
    transaction_factory = MockTransactionFactory()
    network_interface = MockNetworkInterface(crypto_helper, [], [])
    return BlockchainClient(Wallet(wallet_file), transaction_factory,
                            network_interface, crypto_helper)


if __name__ == '__main__':
    client = create_client()
    client.main()
