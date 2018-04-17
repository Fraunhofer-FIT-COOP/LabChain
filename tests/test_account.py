from unittest import TestCase

from labchain.client import BlockchainClient


class MockTransactionFactory:
    pass


class MockNetworkInterface:
    pass


class MockCryptoHelper:
    pass


class CommonTestCase(TestCase):

    def setUp(self):
        self.client = self.create_client()

    @staticmethod
    def create_client():
        return BlockchainClient(MockTransactionFactory(), MockNetworkInterface(), MockCryptoHelper())


class ManageWalletTestCase(CommonTestCase):
    pass


class CreateTransactionTestCase(CommonTestCase):
    pass


class LoadBlockTestCase(CommonTestCase):
    pass
