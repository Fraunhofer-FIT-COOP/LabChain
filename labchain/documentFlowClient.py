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


class Menu:
    """Create a CLI menu with this class."""

    def __init__(self, prompt_text, menu_items, input_text, back_option_label='Go back', fast_exit=False):
        """
        :param prompt_text: A list of string that represent each line of the menu text.
        :param menu_items: A dictionary with the input value as key and a tuple with
                            ('<option description>', <function reference>, <list of args) as value.
        :param input_text: The text at the bottom before the prompt.
        :param back_option_label: The text of the auto created leave menu button.
        :param fast_exit: Set to True to exit after the first input regardless the value.
        """
        self.prompt_text = prompt_text
        self.menu_items = self.__to_ordered_dict(menu_items)
        self.__append_back_menu_item(back_option_label)
        self.input_text = input_text
        self.error_message = ''
        self.fast_exit = fast_exit

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

    def __append_back_menu_item(self, back_option_label):
        self.back_option_key = 'q'
        self.menu_items[self.back_option_key] = (back_option_label, None, None)

    def show(self):
        """Start the menu."""
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
                if self.fast_exit:
                    break
            else:
                self.error_message = 'Wrong input. Please select one of [' + self.__available_options() + '].'


class DoTaskWizard:
    """CLI wizard for making new transactions / do a task /update a task."""

    def __init__(self, wallet, crypto_helper, network_interface):
        self.wallet = wallet
        self.crypto_helper = crypto_helper
        self.network_interface = network_interface



class InitialTransactionWizard:
    """CLI wizard for creating initial transactions."""

    def __init__(self, wallet, crypto_helper, network_interface):
        self.wallet = wallet
        self.crypto_helper = crypto_helper
        self.network_interface = network_interface



class DocumentFlowClient:

    def __init__(self, wallet, network_interface, crypto_helper):
        self.wallet = wallet
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.manage_wallet_menu = Menu(['Manage Person wallet'], {
            '1': ('Show my details', self.__show_my_addresses, []),
            '2': ('Add a new person', self.__create_new_address, []),
            '3': ('Delete a Person', self.__delete_address, [])
        }, 'Please select a value: ', 'Exit Person Wallet')

        self.main_menu = Menu(['Main menu'], {
            '1': ('Manage Persons', self.manage_wallet_menu.show, []),
            '2': ('Create Initial Transaction', self.__create_initial_transaction, []),
            '3': ('doTask', self.__do_task, []),
        }, 'Please select a value: ', 'Exit DocumentFlow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def __create_initial_transaction(self):
        """Ask for all important information to create initial transaction"""
        initial_tx_wizard = InitialTransactionWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface)
        initial_tx_wizard.show()

    def __do_task(self):
        """Ask for all important information to create a new transaction/task and sends it to the network."""
        do_task_wizard = DoTaskWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface)
        do_task_wizard.show()


    def __show_my_addresses(self):
        clear_screen()
        if len(self.wallet) == 0:
            print('Currently there is no person in this task wallet.\n\n')
        else:
            print('Currently following people are in this task wallet:\n\n')
            for label in self.wallet:
                print(label)
                print(self.wallet[label])
                print('\n\n')
        input('Press any key to go back to the main menu!')

    def __create_new_address(self):
        clear_screen()
        label = input('Please add a name for a task:')
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
                               'Please select a key to delete: ', 'Exit without deleting any addresses', True)
            delete_menu.show()
        input('Press any key to go back to the main menu!')


