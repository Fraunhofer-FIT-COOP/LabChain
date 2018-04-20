import os
from collections import OrderedDict


class Wallet:

    def __init__(self, wallet_file):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def __getitem__(self, item):
        pass

    def __delitem__(self, key):
        pass


class Menu:
    def __init__(self, prompt_text, menu_items, input_text):
        self.prompt_text = prompt_text
        self.menu_items = self.to_ordered_dict(menu_items)
        self.input_text = input_text
        self.error_message = ''

    @staticmethod
    def to_ordered_dict(dictionary):
        return OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def available_options(self):
        return ','.join(self.menu_items.keys())

    def print_menu(self):
        self.clear_screen()
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
            self.print_menu()
            input_value = input(self.input_text)
            if input_value in self.menu_items:
                menu_tuple = self.menu_items[input_value]
                # call the menu callback function
                menu_tuple[1](*menu_tuple[2])
                self.error_message = ''
            else:
                self.error_message = 'Wrong input. Please select one of [' + self.available_options() + '].'


class BlockchainClient:

    def __init__(self, wallet, transaction_factory, network_interface, crypto_helper):
        self.wallet = wallet
        self.transaction_factory = transaction_factory
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.manage_wallet_menu = Menu(['prompt text'], {
            '1': ('',),
            '2': ('',),
            '3': ('',),
        }, 'Please select a wallet option')
        self.main_menu = Menu(['Main mneu'], {
            '1': ('Manage Wallet', self.manage_wallet_menu.show, []),
            '2': ('',),
            '3': ('',),
            '4': ('',),
            '5': ('',),
        }, 'Please select a value:')

    def main(self):
        self.main_menu.show()
