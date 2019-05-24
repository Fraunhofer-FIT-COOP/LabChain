import os
import json
from collections import OrderedDict
from labchain.util.utility import Utility

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
        Utility.print_labchain_logo()
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

