import os
from collections import OrderedDict


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

    def __getitem__(self, item):
        key_dict = self.__get_key_dict()
        return key_dict[item]

    def __delitem__(self, key):
        key_dict = self.__get_key_dict()
        del [key]
        self.__save_key_dict(key_dict)

    @staticmethod
    def __csv_to_dict(csv_string):
        result = {}
        for line in csv_string.splitlines():
            label, public_key, private_key = line.split(';', 2)
            result[label] = (public_key, private_key)
        return result

    @staticmethod
    def __dict_to_csv(dictionary):
        result = ''
        for label, key_tuple in dictionary.items():
            public_key, private_key = key_tuple
            result += label + ';' + public_key + ';' + private_key + os.linesep
        return result

    def __save_key_dict(self, key_dict):
        self.wallet_file.seek(0, 0)
        csv = self.__dict_to_csv(key_dict)
        self.wallet_file.write(csv)
        self.wallet_file.flush()

    def __get_key_dict(self):
        wallet_file_contents = self.__get_wallet_file_contents()
        key_dict = self.__csv_to_dict(wallet_file_contents)
        return key_dict

    def get_ordered_key_dict(self):
        wallet_file_contents = self.__get_wallet_file_contents()
        key_dict = self.__csv_to_dict(wallet_file_contents)
        return OrderedDict(sorted(key_dict.items(), key=lambda t: t[0]))

    def __get_wallet_file_contents(self):
        self.wallet_file.seek(0, 0)
        wallet_file_contents = self.wallet_file.read()
        return wallet_file_contents

    def is_empty(self):
        if self.__get_key_dict() is None:
            return True
        else:
            return False


class Menu:
    def __init__(self, prompt_text, menu_items, input_text, back_option_label='Go back'):
        """

        :param prompt_text: A list of string that represent each line of the menu text.
        :param menu_items: A dictionary with the input value as key and a tuple with
                            ('<option description>', <function reference>, <list of args) as value.
        :param input_text: The text at the bottom before the prompt.
        :param back_option_label: The text of the auto created leave menu button.
        """
        self.prompt_text = prompt_text
        self.menu_items = self.__to_ordered_dict(menu_items)
        self.__append_back_menu_item(back_option_label)
        self.input_text = input_text
        self.error_message = ''

    @staticmethod
    def __to_ordered_dict(dictionary):
        return OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))

    def __available_options(self):
        return ','.join(self.menu_items.keys())

    def __print_menu(self):
        clear_screen()
        for line in self.prompt_text:
            print(line)
        print()
        print()
        for opt_index, menu_tuple in self.menu_items.items():
            print(opt_index + ' - ' + menu_tuple[0])
        print()
        print()
        print(self.error_message)

    def show(self):
        while True:
            self.__print_menu()
            input_value = input(self.input_text)
            if input_value in self.menu_items:
                if input_value == self.back_option_key:
                    break
                menu_tuple = self.menu_items[input_value]
                # call the menu callback function
                menu_tuple[1](*menu_tuple[2])
                self.error_message = ''
            else:
                self.error_message = 'Wrong input. Please select one of [' + self.__available_options() + '].'

    def __append_back_menu_item(self, back_option_label):
        max_key = max(self.menu_items, key=int)
        self.back_option_key = str(int(max_key) + 1)
        self.menu_items[self.back_option_key] = (back_option_label, None, None)


class BlockchainClient:

    def __init__(self, wallet, transaction_factory, network_interface, crypto_helper):
        self.wallet = wallet
        self.transaction_factory = transaction_factory
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.manage_wallet_menu = Menu(['prompt text'], {
            '1': ('Show own addresses',),
            '2': ('Create new addresses',),
            '3': ('Delete address',),
        }, 'Please select a wallet option: ')
        self.main_menu = Menu(['Main menu'], {
            '1': ('Manage Wallet', self.manage_wallet_menu.show, []),
            '2': ('Create Transaction', self.__create_transaction, []),
            '3': ('Load Block', self.__load_block, []),
            '4': ('Load Transaction', self.__load_transaction, []),
        }, 'Please select a value: ', 'Exit Blockchain Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def __create_transaction(self):
        """Asks for all important information to create a new transaction and sends it to the network"""

        def validate_sender_input(usr_input):
            try:
                int_usr_input = int(usr_input)
            except ValueError:
                return False

            if int_usr_input != 0 and int_usr_input <= len(self.wallet.get_ordered_key_dict()):
                return True
            else:
                return False

        def validate_receiver_input(usr_input):
            # TODO
            if usr_input == str(1):
                return True
            else:
                return False

        def validate_payload_input(usr_input):
            # TODO
            if usr_input == str(1):
                return True
            else:
                return False

        def ask_for_key_from_wallet():
            # retrieve dict with current keys in the wallet
            wallet_key_dict = self.wallet.get_ordered_key_dict()

            print(u'Current keys in the wallet: ')
            counter = 0
            for key, value_tuple in wallet_key_dict.items():
                counter += 1
                print (str(counter) + u': ' + str(key))
                print (u'Private Key: ' + str(value_tuple[0]))
                print (u'Public Key: ' + str(value_tuple[1]))
                print ()

            user_input = input('Please choose a sender account (by number): ')
            return user_input

        def ask_for_receiver():
            usr_input = input('Please type in a receiver address: ')
            return usr_input

        def ask_for_payload():
            usr_input = input('Please type in a payload: ')
            return usr_input

        # actual function code
        clear_screen()

        # check if wallet contains any keys
        # case: wallet not empty
        if not self.wallet.is_empty():
            chosen_key = False
            chosen_receiver = False
            chosen_payload = False

            # ask for valid sender input in a loop
            while not validate_sender_input(chosen_key):
                chosen_key = ask_for_key_from_wallet()
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print (str(chosen_key))

            while not validate_receiver_input(chosen_receiver):
                chosen_receiver = ask_for_receiver()
                clear_screen()
                print('Invalid input! Please choose a correct receiver!')
                print()
            print (str(chosen_receiver))

            while not validate_payload_input(chosen_payload):
                chosen_payload = ask_for_payload()
                clear_screen()
                print('Invalid input! Please choose a correct payload!')
                print()
            print (str(chosen_payload))

        # case: wallet is empty
        else:
            print(u'Wallet does not contain any keys! Please create one first!')

        input('Press any key to go back to the main menu!')

    def __load_block(self):
        def str_represents_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        def read_blockchain_number():
            return input('Please input the block number you are looking for (Blocks are numbered starting at zero)!')

        clear_screen()
        input_str = read_blockchain_number()

        while not str_represents_int(input_str) or not int(input_str) >= 0:
            if input_str == '':
                # show main menu
                return
            print("Invalid Input. Numbers starting from 0 are allowed.")
            print()
            input_str = read_blockchain_number()

        clear_screen()
        block = self.network_interface.requestBlock(int(input_str))
        if block is not None:
            print('block number: ' + str(block.number))
            print('merkle tree: ' + str(block.merkle_tree))
            print('transactions: ' + str(block.transactions))
            print('nonce: ' + str(block.nonce))
            print('creator: ' + str(block.creator))
        else:
            print('There is no block with the given number.')

        print()
        input('Press any key to go back to the main menu!')

    def __load_transaction(self):
        """Prompt the user for a transaction hash and display the transaction details."""
        clear_screen()
        transaction_hash = input('Please enter a transaction hash: ')
        transaction = self.network_interface.requestTransaction(transaction_hash)

        clear_screen()
        if not transaction:
            print('Transaction does not exist')
        else:
            print('Sender ID: {}'.format(transaction.sender))
            print('Receiver ID: {}'.format(transaction.receiver))
            print('Payload: {}'.format(transaction.payload))
            print('Signature: {}'.format(transaction.signature))
        print()
        # wait for any input before returning to menu
        input('Press enter to continue...')
