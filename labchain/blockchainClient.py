import os

from labchain.datastructure.transaction import Transaction
from labchain.network.networking import TransactionDoesNotExistException, \
    BlockDoesNotExistException, NoPeersException
from labchain.util.Menu import Menu


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


class Wallet:

    def __init__(self, wallet_file):
        self.wallet_file = wallet_file

    def __setitem__(self, key, value):
        key_dict = self.__get_key_dict()
        key_dict[key] = value
        self.__save_key_dict(key_dict)

    def __iter__(self):
        key_dict = self.__get_key_dict()
        return key_dict.__iter__()

    def __len__(self):
        key_dict = self.__get_key_dict()
        return len(key_dict.keys())

    def __contains__(self, label):
        key_dict = self.__get_key_dict()
        return label in key_dict

    def __getitem__(self, item):
        key_dict = self.__get_key_dict()
        return key_dict[item]

    def __delitem__(self, key):
        key_dict = self.__get_key_dict()
        del key_dict[key]
        self.__save_key_dict(key_dict)

    @staticmethod
    def __csv_to_dict(csv_string):
        result = {}
        for line in csv_string.splitlines():
            try:
                label, public_key, private_key = line.split(';', 2)
                result[label] = (public_key, private_key)
            except ValueError:
                pass
        return result

    @staticmethod
    def __dict_to_csv(dictionary):
        result = ''
        for label in sorted(list(dictionary.keys())):
            public_key, private_key = dictionary[label]
            result += label + ';' + public_key + ';' + private_key + os.linesep
        return result

    def __save_key_dict(self, key_dict):
        self.wallet_file.seek(0, 0)
        self.wallet_file.truncate()
        csv = self.__dict_to_csv(key_dict)
        self.wallet_file.write(csv)
        self.wallet_file.flush()

    def __get_key_dict(self):
        wallet_file_contents = self.__get_wallet_file_contents()
        key_dict = self.__csv_to_dict(wallet_file_contents)
        return key_dict

    def __get_wallet_file_contents(self):
        self.wallet_file.seek(0, 0)
        wallet_file_contents = self.wallet_file.read()
        return wallet_file_contents


class TransactionWizard:
    """CLI wizard for creating new transactions."""

    def __init__(self, wallet, crypto_helper, network_interface):
        self.wallet = wallet
        self.crypto_helper = crypto_helper
        self.network_interface = network_interface

    def __wallet_to_list(self):
        wallet_list_result = []
        for key in sorted(self.wallet):
            wallet_list_result.append([str(key), self.wallet[key][0], self.wallet[key][1]])
        return wallet_list_result

    def __validate_sender_input(self, usr_input):
        try:
            int_usr_input = int(usr_input)
        except ValueError:
            return False

        if int_usr_input != 0 and int_usr_input <= len(self.wallet):
            return True
        else:
            return False

    @staticmethod
    def __validate_receiver_input(usr_input):
        if len(usr_input) > 0:
            return True
        else:
            return False

    @staticmethod
    def __validate_payload_input(usr_input):
        if len(usr_input) > 0:
            return True
        else:
            return False

    @staticmethod
    def __ask_for_key_from_wallet(wallet_list):
        print(u'Current keys in the wallet: ')
        for counter, key in enumerate(wallet_list, 1):
            print()
            print(str(counter) + u':\t' + str(key[0]))
            print(u'\tPrivate Key: ' + str(key[2]))
            print(u'\tPublic Key: ' + str(key[1]))
            print()

        user_input = input('Please choose a sender account (by number) or press enter to return: ')
        return user_input

    @staticmethod
    def __ask_for_receiver():
        usr_input = input('Please type in a receiver address: ')
        return str(usr_input)

    @staticmethod
    def __ask_for_payload():
        usr_input = input('Please type in a payload: ')
        return str(usr_input)

    def show(self):
        """Start the wizard."""
        clear_screen()

        # convert dict to an ordered list
        # this needs to be done to get an ordered list that does not change
        # at runtime of the function
        wallet_list = self.__wallet_to_list()

        # check if wallet contains any keys
        # case: wallet not empty
        if not len(self.wallet) == 0:
            chosen_key = self.__ask_for_key_from_wallet(wallet_list)
            if chosen_key == '':
                return

            # ask for valid sender input in a loop
            while not self.__validate_sender_input(chosen_key):
                chosen_key = self.__ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print(u'Sender: ' + str(chosen_key))
            chosen_receiver = self.__ask_for_receiver()

            while not self.__validate_receiver_input(chosen_receiver):
                # clear_screen()
                print('Invalid input! Please choose a correct receiver!')
                print(u'Sender: ' + str(chosen_key))
                chosen_receiver = self.__ask_for_receiver()
                print()

            clear_screen()
            print(u'Sender: ' + str(chosen_key))
            print(u'Receiver: ' + str(chosen_receiver))
            chosen_payload = self.__ask_for_payload()

            while not self.__validate_payload_input(chosen_payload):
                # clear_screen()
                print('Invalid input! Please choose a correct payload!')
                print(u'Sender: ' + str(chosen_key))
                print(u'Receiver: ' + str(chosen_receiver))
                chosen_payload = self.__ask_for_payload()
                print()

            clear_screen()

            # Create transaction Object and send to network
            private_key = wallet_list[int(chosen_key) - 1][2]
            public_key = wallet_list[int(chosen_key) - 1][1]

            new_transaction = Transaction(str(public_key), str(chosen_receiver), str(chosen_payload))
            new_transaction.sign_transaction(self.crypto_helper, private_key)
            transaction_hash = self.crypto_helper.hash(new_transaction.get_json())

            self.network_interface.sendTransaction(new_transaction)

            print('Transaction successfully created!')
            print()
            print(u'Sender: ' + public_key)
            print(u'Receiver: ' + str(chosen_receiver))
            print(u'Payload: ' + str(chosen_payload))
            print(u'Hash: ' + str(transaction_hash))
            print()

        # case: wallet is empty
        else:
            print(u'Wallet does not contain any keys! Please create one first!')

        input('Press any key to go back to the main menu!')


class BlockchainClient:

    def __init__(self, wallet, network_interface, crypto_helper):
        self.wallet = wallet
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.manage_wallet_menu = Menu(['Manage wallet'], {
            '1': ('Show my addresses', self.__show_my_addresses, []),
            '2': ('Create new address', self.__create_new_address, []),
            '3': ('Delete address', self.__delete_address, [])
        }, 'Please select a value: ', 'Exit Wallet Menu')
        self.load_block_menu = Menu(['Load Block'], {
            '1': ('Load by number', self.__load_block, [False]),
            '2': ('Load by hash', self.__load_block, [True])
        }, 'Please select a value: ', 'Exit Load Block Menu')
        self.load_transaction_menu = Menu(['Load Transaction'], {
            '1': ('Load by hash', self.__load_transaction_by_hash, []),
            '2': ('Show Transaction Pool', self.__show_transaction_pool, []),
            '3': ('Show n last transactions',
                  self.__search_transaction_from_sender, []),
            '4': ('Load by receiver\'s public key',
                  self._show_transaction_by_public_key, ["receiver"]),
            '5': ('Load by sender\'s public key',
                  self._show_transaction_by_public_key, ["sender"]),
            '6': ('Show all transactions',
                  self._show_transaction_by_public_key, [])
        }, 'Please select a value: ', 'Exit Load Transaction Menu')
        self.main_menu = Menu(['Main menu'], {
            '1': ('Manage Wallet', self.manage_wallet_menu.show, []),
            '2': ('Create Transaction', self.__create_transaction, []),
            '3': ('Load Block', self.load_block_menu.show, []),
            '4': ('Transaction Menu', self.load_transaction_menu.show, []),
            '5': ('Show Connected Peers', self.__load_peers, []),
        }, 'Please select a value: ', 'Exit Blockchain Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def __create_transaction(self):
        """Ask for all important information to create a new transaction and sends it to the network."""
        transaction_wizard = TransactionWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface)
        transaction_wizard.show()

    def __show_my_addresses(self):
        clear_screen()
        if len(self.wallet) == 0:
            print('Currently you have no addresses in your wallet.\n\n')
        else:
            print('Currently you have the following addresses in your wallet:\n\n')
            for label in self.wallet:
                print(label)
                print(self.wallet[label])
                print('\n\n')
        input('Press any key to go back to the main menu!')

    def __create_new_address(self):
        clear_screen()
        label = input('Please create a name for your new address:')
        if len(label) == 0:
            print('Name should not be empty')
        elif label in self.wallet:
            print('Name should be unique!')
            print('Address <' + label + '> already exists')
        else:
            pr_key, pub_key = self.crypto_helper.generate_key_pair()
            self.wallet[label] = (pub_key, pr_key)
            print('New address <' + label + '> created.')
        input('Press any key to go back to the main menu!')

    def __delete_by_label(self, label):
        del self.wallet[label]
        print('Address <' + label + '> was deleted from your wallet.')

    def __delete_address(self):
        clear_screen()
        if len(self.wallet) == 0:
            print('Currently you have no addresses in your wallet.\n\n')
        else:
            i = 1
            addresses = {}
            for label in sorted(self.wallet):
                addresses[str(i)] = (label, self.__delete_by_label, [label, ])
                i += 1
            delete_menu = Menu(['Delete address'], addresses,
                               'Please select a key to delete: ',
                               'Exit without deleting any addresses', True)
            delete_menu.show()
        input('Press any key to go back to the main menu!')

    def __load_block(self, by_hash=False):
        def str_represents_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        def read_blockchain_number():
            if by_hash:
                return input('Please input the block hash you are looking for: ')
            else:
                return input(
                    'Please input the block number you are looking for (Blocks are numbered starting at zero): ')

        clear_screen()
        input_str = read_blockchain_number()

        if not by_hash:
            while not str_represents_int(input_str) or not int(input_str) >= 0:
                if input_str == '':
                    # show main menu
                    return
                print("Invalid Input. Numbers starting from 0 are allowed.")
                print()
                input_str = read_blockchain_number()

        clear_screen()
        try:
            if by_hash:
                blocks = [self.network_interface.requestBlockByHash(input_str)]
            else:
                blocks = self.network_interface.requestBlock(int(input_str))
        except BlockDoesNotExistException:
            blocks = []
        if not blocks:
            print('There is no block with the given number.')
        else:
            for block in blocks:
                if block is not None:
                    print('block number: ' + str(block.block_id))
                    print('timestamp: ' + str(block.timestamp))
                    print('predecessor hash: ' + str(block.predecessor_hash))
                    print('merkle tree: ' + str(block.merkle_tree_root))
                    print('transactions: ' + ', '.join([str(transaction) for transaction in block.transactions]))
                    print('nonce: ' + str(block.nonce))
                    print('creator: ' + str(block.block_creator_id))

        print()
        input('Press any key to go back to the main menu!')

    def __load_transaction_by_hash(self):
        """Prompt the user for a transaction hash and display the transaction details."""
        clear_screen()
        transaction_hash = input('Please enter a transaction hash: ')
        try:
            transaction, block_hash = self.network_interface.requestTransaction(transaction_hash)
        except TransactionDoesNotExistException:
            transaction, block_hash = None, None

        clear_screen()
        if not transaction:
            print('Transaction does not exist.')
        else:
            transaction.print()
            print()
            print('Block Hash: {}'.format(block_hash))
        print()
        # wait for any input before returning to menu
        input('Press enter to continue...')

    def __load_n_last_transactions(self):
        """Prompt the user for a n: number of transactions"""
        clear_screen()
        n = input('Please enter n: ')

        transactions = self.network_interface.get_n_last_transactions(n)

        clear_screen()

        if not transactions:
            print ("No transactions")
        else:
            for transaction in transactions:
                transaction.print()
                print()
        input('Press enter to continue...')

    def __search_transaction_from_receiver(self):
        """Prompt the user for a public key: public key of the reciver"""
        clear_screen()
        receiver_public_key = input('Please enter reciver public key: ')
        transactions = self.network_interface.search_transaction_from_receiver(receiver_public_key)

        clear_screen()

        if not transactions:
            print ("No transactions")
        else:
            for transaction in transactions:
                transaction.print()
                print()
        input('Press enter to continue...')



    def __search_transaction_from_sender(self):
        """Prompt the user for a public key: public key of the reciver"""
        clear_screen()
        sender_public_key = input('Please enter sender public key: ')
        transactions = self.network_interface.search_transaction_from_sender(sender_public_key)
        
        clear_screen()

        if not transactions:
            print ("No transactions")
        else:
            for transaction in transactions:
                transaction.print()
                print()
        input('Press enter to continue...')

    def __show_transaction_pool(self):
        clear_screen()
        transactions = self.network_interface.requestTransactionsInPool()
        if len(transactions) > 0:
            print('There are {} transactions in the txpool:'.format(str(len(transactions))))
            for transaction in transactions:
                transaction.print()
                print()
        else:
            print("Transaction pool is empty.")
            print()
        input('Press enter to continue...')

    def __load_peers(self):
        """display the peers list."""
        clear_screen()
        try:
            print('peers : {}'.format(self.network_interface._connected_peers()))
        except NoPeersException:
            print('No peers found')
        print()
        # wait for any input before returning to menu
        input('Press enter to continue...')

    def _show_transaction_by_public_key(self, Owner_Of_publicKey = ""):
        """Show received/sent transaction by receiver's/sender's public key."""
        """If Owner_of_publicKey = "", show all transactions."""
        clear_screen()
        if Owner_Of_publicKey != "":
            public_key = input('Please enter a ' + Owner_Of_publicKey + ' address: ')

        transactions = self.network_interface.requestAllTransactions()

        transaction_exist = False
        clear_screen()

        if Owner_Of_publicKey == "sender":
            for transaction in transactions:
                if public_key == transaction.sender:
                    transaction_exist = True

                    transaction.print()
                    print()
        if Owner_Of_publicKey == "receiver":
            for transaction in transactions:
                if public_key == transaction.receiver:
                    transaction_exist = True

                    transaction.print()
                    print()
        if Owner_Of_publicKey == "":
            if transactions:
                transaction_exist = True
            for transaction in transactions:
                transaction.print()
                print()

        if transaction_exist == False:
            print('Transaction does not exist')
        # wait for any input before returning to menu
        input('Press enter to continue...')
