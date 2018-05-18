import os
import sys
from io import StringIO
from unittest import TestCase

from labchain.block import Block
from labchain.client import BlockchainClient, Wallet
from labchain.transaction import Transaction


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
            if block.block_id == block_number:
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

    def generate_key_pair(self):
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
        # prevent warning in output
        if 'TERM' not in os.environ:
            os.environ['TERM'] = 'xterm-color'
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
        self.mock_network_interface = MockNetworkInterface(self.mock_crypto_helper, self.transactions, self.blocks)
        return BlockchainClient(Wallet(self.wallet_file), self.mock_network_interface, self.mock_crypto_helper)

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
        self.wallet_file.write(label + ';' + public_key + ';' + private_key + '\n')
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

    def test_show_own_addresses_with_two_addresses(self):
        """ Test case: #1
            Tested requirement: #170
        """
        # given
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 1', pub_key, pr_key)
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 2', pub_key, pr_key)
        # when
        self.queue_input('1')
        self.queue_input('1')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('test key 1')
        self.assert_string_in_output('test key 2')

    def test_show_own_addresses_with_empty_wallet(self):
        """ Test case: #2
            Tested requirement: #170
        """
        # when
        self.queue_input('1')
        self.queue_input('1')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('no addresses in your wallet')

    def test_create_new_address_with_non_empty_name(self):
        """ Test case: #3
            Tested requirement: #160
        """
        # when
        self.queue_input('1')
        self.queue_input('2')
        self.queue_input('test key')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        addresses = self.get_wallet_key_pairs()
        self.assertEqual(len(addresses), 1)
        label, pub_key, pr_key = addresses[0]
        self.assertEqual(label, 'test key')
        self.assertTrue(pub_key)
        self.assertTrue(pr_key)

    def test_create_new_address_with_empty_name(self):
        """ Test case: #3a
            Tested requirement: #160
        """
        # when
        self.queue_input('1')
        self.queue_input('2')
        self.queue_input('')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('Name should not be empty')

    def test_create_new_address_with_one_existing_key(self):
        """ Test case: #4
            Tested requirement: #160
        """
        # given
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('existing key', pub_key, pr_key)
        # when
        self.queue_input('1')
        self.queue_input('2')
        self.queue_input('test key')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        addresses = self.get_wallet_key_pairs()
        self.assertEqual(len(addresses), 2)
        label, _, _ = addresses[0]
        self.assertEqual(label, 'existing key')
        label, pub_key, pr_key = addresses[1]
        self.assertEqual(label, 'test key')
        self.assertTrue(pub_key)
        self.assertTrue(pr_key)

    def test_create_not_unique_address_with_one_existing_key(self):
        """ Test case: #4a
            Tested requirement: #160
        """
        # given
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('existing key', pub_key, pr_key)
        # when
        self.queue_input('1')
        self.queue_input('2')
        self.queue_input('existing key')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('Name should be unique!')

    def test_delete_address_with_empty_wallet(self):
        """ Test case: #5
            Tested requirement: #170
        """
        # when
        self.queue_input('1')
        self.queue_input('3')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('no addresses in your wallet')

    def test_show_addresses_which_can_be_deleted_with_two_addresses(self):
        """ Test case: #6
            Tested requirement: #170
        """
        # given
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 1', pub_key, pr_key)
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 2', pub_key, pr_key)
        # when
        self.queue_input('1')
        self.queue_input('3')
        self.queue_input('3')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        self.assert_string_in_output('test key 1')
        self.assert_string_in_output('test key 2')

    def test_delete_address_with_two_addresses(self):
        """ Test case: #7
            Tested requirement: #170
        """
        # given
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 1', pub_key, pr_key)
        pr_key, pub_key = self.mock_crypto_helper.generatePair()
        self.store_key_pair_in_wallet('test key 2', pub_key, pr_key)
        # when
        self.queue_input('1')
        self.queue_input('3')
        self.queue_input('2')
        self.queue_input('')
        self.queue_input('4')
        self.queue_input('5')
        self.client.main()
        # then
        addresses = self.get_wallet_key_pairs()
        self.assertEqual(len(addresses), 1)
        label, _, _ = addresses[0]
        self.assertEqual(label, 'test key 1')
        self.assert_string_in_output('<test key 2> was deleted')


class CreateTransactionTestCase(CommonTestCase):

    def test_create_transaction_with_valid_input(self):
        """ Test Case: 8
            Test requirement: 180, 190
        """
        # given
        self.store_key_pair_in_wallet('DrugMoneyKey', 'public_123', 'private_456')
        self.store_key_pair_in_wallet('BestLabel', 'public_555', 'private_111')
        valid_signature = self.mock_crypto_helper.sign('private_111', 'public_555' + 'test_receiver' + 'test_payload')
        # when
        self.queue_input('2')  # go to menu 2
        self.queue_input('2')  # choose label 2
        self.queue_input('test_receiver')  # input receiver address
        self.queue_input('test_payload')  # input payload
        self.queue_input('')  # press Enter
        # end of test case input
        self.queue_input('5')  # quit client now
        self.client.main()
        # then
        self.assertEqual(len(self.transactions), 1)
        self.assertEqual(self.transactions[0].sender, 'public_555')
        self.assertEqual(self.transactions[0].receiver, 'test_receiver')
        self.assertEqual(self.transactions[0].payload, 'test_payload')
        self.assertEqual(self.transactions[0].signature, valid_signature)

    def test_create_transaction_with_invalid_key_pair_index_as_sender(self):
        """ Test Case: 8a
            Test requirement: 180, 190
        """
        # given
        self.store_key_pair_in_wallet('DrugMoneyKey', 'public_123', 'private_45')
        self.store_key_pair_in_wallet('BestLabel', 'public_555', 'private_111')
        # when
        self.queue_input('2')
        self.queue_input('3')
        # end of test case input
        # finish with valid input and quit client
        self.queue_input('2')
        self.queue_input('test_receiver')  # input receiver address
        self.queue_input('test_payload')  # input payload
        self.queue_input('')  # press Enter
        self.queue_input('5')  # quit client now
        self.client.main()
        # then
        self.assert_string_in_output('Invalid input! Please choose a correct index!')

    def test_create_transaction_with_invalid_receiver_address(self):
        """ Test Case: 8b
            Test requirement: 180, 190
        """
        # given
        self.store_key_pair_in_wallet('DrugMoneyKey', 'public_123', 'private_45')
        self.store_key_pair_in_wallet('BestLabel', 'public_555', 'private_111')
        # when
        self.queue_input('2')
        self.queue_input('2')
        self.queue_input('')
        # end of test case input
        # finish with valid input and quit client
        self.queue_input('test_receiver')  # input receiver address
        self.queue_input('test_payload')  # input payload
        self.queue_input('')  # press Enter
        self.queue_input('5')  # quit client now
        self.client.main()
        # then
        self.assert_string_in_output('Invalid input! Please choose a correct receiver!')

    def test_create_transaction_with_invalid_payload(self):
        """ Test Case: 8c
            Test requirement: 180, 190
        """
        # given
        self.store_key_pair_in_wallet('DrugMoneyKey', 'public_123', 'private_45')
        self.store_key_pair_in_wallet('BestLabel', 'public_555', 'private_111')
        # when
        self.queue_input('2')
        self.queue_input('2')
        self.queue_input('test_receiver')
        self.queue_input('')
        # end of test case input
        # finish with valid input and quit client
        self.queue_input('test_payload')  # input payload
        self.queue_input('')  # press Enter
        self.queue_input('5')  # quit client now
        self.client.main()
        # then
        self.assert_string_in_output('Invalid input! Please choose a correct payload!')


class TransactionTestCase(CommonTestCase):

    def test_show_transaction_with_existing_transaction(self):
        """ Test case: #11
            Tested requirement: #200
        """
        # given
        transaction = Transaction('some_sender_id', 'some_receiver_id', 'some_payload', 'some_signature')
        self.add_transaction(transaction)
        transaction_hash = self.mock_crypto_helper.hash_transaction(transaction)
        # when
        self.queue_input('4')
        self.queue_input(transaction_hash)
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


class LoadBlockTestCase(CommonTestCase):

    def test_request_block_from_blockchain_with_empty_block_id(self):
        """ Test case: #9
            Tested requirement: #210
        """
        # given
        #     blockchain is empty -> nothing to setup
        # when
        self.queue_input('3')
        self.queue_input('')  # press enter
        # at this point the main menu is shown
        self.queue_input('5')  # exit blockchain client
        self.client.main()
        # then
        # check if submenu 3 was printed
        self.assert_string_in_output(
            'Please input the block number you are looking for (Blocks are numbered starting at zero)!')
        # check if main menu is shown
        self.assert_string_in_output('Main menu')

    def test_request_block_from_blockchain_although_blockchain_is_empty(self):
        """ Test case: #10a
            Tested requirement: #210
        """
        # given
        # blockchain is empty -> nothing to setup

        # when
        self.queue_input('3')
        self.queue_input('1')
        self.queue_input('')  # press enter
        self.queue_input('5')
        self.client.main()

        # then
        self.assert_string_in_output('There is no block with the given number.')

    def test_request_block_from_nonempty_blockchain(self):
        """ Test case: #10
            Tested requirement: #210
        """

        # given
        transactions = []
        for i in range(5):
            transactions.append(Transaction("test_sender", "test_receiver", "payload_data"))

        block0 = Block(0, "merkle_tree_hash_qthq4thi4q4t", 'pred_hash_1', "creator_hash", transactions, 123)
        block1 = Block(1, "merkle_tree_hash_qthq5thi4q1t", 'pred_hash_2', "creator_hash", transactions, 456, )
        self.add_block(block0)
        self.add_block(block1)

        # when
        self.queue_input('3')
        self.queue_input('1')
        self.queue_input('')  # press enter
        self.queue_input('5')
        self.client.main()

        # then
        self.assert_string_in_output('1')  # block number
        self.assert_string_in_output('merkle_tree_hash_qthq5thi4q1t')  # merkle tree root
        self.assert_string_in_output('pred_hash_2')  # predecessor hash
        self.assert_string_in_output('456')  # nonce
        self.assert_string_in_output('creator_hash')  # block creator
