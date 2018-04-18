import sys
from io import StringIO
from unittest import TestCase

from labchain.client import BlockchainClient, Wallet


class MockTransaction:
    def __init__(self, sender, receiver, payload):
        self.sender = sender
        self.receiver = receiver
        self.payload = payload
        self.signature = None

    def signTransaction(self, signature):
        self.signature = signature

    def validateTransaction(self):
        return True


class MockTransactionFactory:
    def createTransaction(self, sender, receiver, payload):
        return MockTransaction(sender, receiver, payload)


class MockNetworkInterface:
    def __init__(self, transactions, blocks):
        self.transactions = transactions
        self.blocks = blocks

    def sendTransaction(self, transaction):
        self.transactions.append(transaction)

    def sendBlock(self, block):
        self.blocks.append(block)

    def onBlockReceived(self):
        pass

    def onTransactionReceived(self):
        pass

    def requestBootstrap(self):
        return None

    def requestTransaction(self, hash):
        pass

    def requestBlock(self, block_id):
        pass


class MockCryptoHelper:

    def __init__(self):
        self.key_counter = 1
        self.hash_counter = 1
        self.hash_map = {}

    def sign(self, private_key, message):
        return message + ' Signed with: ' + private_key

    def validate(self, public_key, message):
        message, private_key = message.split(' Signed with: ', 1)
        # valid if private key is reversed public key
        return public_key == private_key[::-1]

    def generatePair(self):
        public_key = '{num:05d}'.format(num=self.key_counter)
        # private key is the reversed public key
        private_key = public_key[::-1]
        self.key_counter += 1
        return private_key, public_key

    def hash(self, message):
        if message not in self.hash_map:
            self.hash_map[message] = '{num:05d}'.format(num=self.hash_counter)
            self.hash_counter += 1
        return self.hash_map[message]


class CommonTestCase(TestCase):
    """Common test superclass for utilities."""

    def setUp(self):
        self.__stdout_original = sys.stdout
        self.__stdin_original = sys.stdin
        self.output_buffer = StringIO()
        self.input_buffer = StringIO()
        sys.stdout = self.output_buffer
        sys.stdin = self.input_buffer
        self.client = self.create_client()

    def tearDown(self):
        sys.stdout = self.__stdout_original
        sys.stdin = self.__stdin_original

    def create_client(self):
        """Create a BlockchainClient instance supplied with mocked dependencies."""
        self.wallet_file = StringIO()
        self.transactions = []
        self.blocks = []
        return BlockchainClient(Wallet(self.wallet_file), MockTransactionFactory(),
                                MockNetworkInterface(self.transactions, self.blocks),
                                MockCryptoHelper())

    def get_output(self):
        """Get the whole stdout content since the start of the test. """
        return self.output_buffer.getvalue().splitlines()

    def assert_line_in_output(self, line):
        """Assert that this line has been written to stdout since the start of the test."""
        self.assertIn(line, self.get_output())

    def queue_input(self, line):
        """Queue an input to stdin to be retrieved later by an "input()" call.

        Make sure tu queue all inputs BEFORE running the actual program.
        Also do not query less inputs than the code will try to read.
        Else you will get: EOFError: EOF when reading a line
        """
        # go to end of buffer
        self.input_buffer.seek(0, 2)
        # append to buffer
        self.input_buffer.write(line + '\n')
        # reset cursor position to start of buffer
        self.input_buffer.seek(0)

    def get_wallet_file_content(self):
        """Return a list of lines from the wallet file."""
        return self.wallet_file.getvalue().splitlines()


class ManageWalletTestCase(CommonTestCase):
    pass


class CreateTransactionTestCase(CommonTestCase):
    pass


class TransactionTestCase(CommonTestCase):
    pass


class LoadBlockTestCase(CommonTestCase):
    pass


class UnnecessaryTestCase(CommonTestCase):
    """Just for demonstration.

    TODO: Remove before merging
    """

    def test_output_mock(self):
        print("test")
        self.assert_line_in_output('test')

    def test_input_mock(self):
        """Make sure tu make all inputs BEFORE running the actual program.

        Also do not query less inputs than the code will try to read.
        Else you will get: EOFError: EOF when reading a line
        """
        self.queue_input('test')
        self.queue_input('test2')
        input_str = input('Please input something')
        input_str2 = input('Please input something')
        self.assertEqual('test', input_str)
        self.assertEqual('test2', input_str2)
