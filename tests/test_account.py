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


class MockBlock:
    def __init__(self, number, merkle_tree, transactions, nonce, creator):
        self.number = number
        self.merkle_tree = merkle_tree
        self.transactions = transactions
        self.nonce = nonce
        self.creator = creator


class MockTransactionFactory:
    def createTransaction(self, sender, receiver, payload):
        return MockTransaction(sender, receiver, payload)


class MockNetworkInterface:
    def __init__(self, crypto_helper, transactions, blocks):
        self.crypto_helper = crypto_helper
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
        for transaction in self.transactions:
            if self.crypto_helper.hash_transaction(transaction) == hash:
                return transaction

    def requestBlock(self, block_number):
        for block in self.blocks:
            if block.number == block_number:
                return block
        return None


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

    def hash_transaction(self, transaction):
        return self.hash(transaction.sender + transaction.receiver + transaction.payload + transaction.signature)


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
        self.mock_crypto_helper = MockCryptoHelper()
        self.mock_transaction_factory = MockTransactionFactory()
        self.mock_network_interface = MockNetworkInterface(self.mock_crypto_helper, self.transactions, self.blocks)
        return BlockchainClient(Wallet(self.wallet_file), self.mock_transaction_factory,
                                self.mock_network_interface, self.mock_crypto_helper)

    def get_raw_output(self):
        """Get the whole stdout content since the start of the test as raw string. """
        return self.output_buffer.getvalue()

    def get_output(self):
        """Get the whole stdout content since the start of the test as list of lines. """
        return self.get_raw_output().splitlines()

    def assert_line_in_output(self, line):
        """Assert that this line has been written to stdout since the start of the test."""
        self.assertIn(line, self.get_output())

    def assert_string_in_output(self, string):
        """Assert that this line has been written to stdout since the start of the test."""
        self.assertIn(string, self.get_raw_output())

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

    def store_key_pair_in_wallet(self, label, public_key, private_key):
        """Stores a labeled key pair in the mocked wallet file.

        The format is CSV: <label>;<public_key>;<private_key>
        """
        # go to end of file
        self.wallet_file.seek(0, 2)
        self.wallet_file.write(label + ';' + public_key + ';' + private_key)
        # go to the beginning of the file
        self.wallet_file.seek(0, 0)

    def get_wallet_key_pairs(self):
        """Return a list of key pair tuples.

        A key pair tuple is structured as follows (<label>, <public_key>, <private_key>).
        """
        wallet_content = []
        for line in self.get_wallet_file_content():
            label, public_key, private_key = line.split(';', 2)
            wallet_content.append((label, public_key, private_key))
        return wallet_content

    def get_wallet_key_pair_by_label(self, label):
        """Return a (<public_key>, <private_key>) tuple, if there is a key pair with this label.

        Returns (None, None) otherwise.
        """
        wallet_content = self.get_wallet_key_pairs()
        for key_tuple in wallet_content:
            if key_tuple[0] == label:
                return key_tuple[1].key_tuple[2]
        return None, None

    def add_transaction(self, transaction):
        """Add a transaction to all transactions in the blockchain."""
        self.transactions.append(transaction)

    def add_block(self, block):
        """Add a block to all blocks in the blockchain."""
        self.blocks.append(block)


class ManageWalletTestCase(CommonTestCase):
    pass


class CreateTransactionTestCase(CommonTestCase):
    pass


class TransactionTestCase(CommonTestCase):
    pass


class LoadBlockTestCase(CommonTestCase):
    def test_request_block_from_blockchain_although_blockchain_is_empty(self):
        """ Test case: #10
            Tested requirement: #210
        """
        pass

    def test_request_block_from_nonempty_blockchain(self):
        """ Test case: #10a
            Tested requirement: #210
        """

        # given
        transactions = []
        for i in range(5):
            transactions.append(MockTransaction("test_sender", "test_receiver", "payload_data"))

        block0 = MockBlock(0, "merkle_tree_hash_qthq4thi4q4t", transactions, "nonce_hash", "creator_hash")
        block1 = MockBlock(1, "merkle_tree_hash_qthq5thi4q1t", transactions, "nonce_hash", "creator_hash")
        self.add_block(block0)
        self.add_block(block1)

        # when
        self.queue_input('3')
        self.queue_input('1')
        self.queue_input('')  # press enter
        self.client.main()

        # then
        self.assert_string_in_output('1')  # block number
        self.assert_string_in_output('merkle_tree_hash_qthq4thi4q4t')  # merkle tree root
        self.assert_string_in_output('nonce_hash')  # merkle tree root
        self.assert_string_in_output('creator_hash')  # block creator


    def test_show_transaction_with_existing_transaction(self):
        """ Test case: #11
            Tested requirement: #200
        """
        # given
        transaction = MockTransaction('some_sender_id', 'some_receiver_id', 'some_payload')
        transaction.signTransaction('some_signature')
        self.add_transaction(transaction)
        # when
        self.queue_input('4')
        self.queue_input('1a2b')
        self.queue_input('')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('some_sender_id')
        self.assert_string_in_output('some_receiver_id')
        self.assert_string_in_output('some_sender_id')
        self.assert_string_in_output('some_payload')

    def test_show_transaction_with_nonexisting_transaction(self):
        """ Test case: #11a
            Tested requirement: #200
        """
        # when
        self.queue_input('4')
        self.queue_input('1a2b')
        self.queue_input('')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('Transaction does not exist')




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
        self.assertEqual('test2', input_str2)
        self.assertEqual('test', input_str)
