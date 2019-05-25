import os
import json
from collections import OrderedDict
import copy

from labchain.datastructure.taskTransaction import TaskTransaction

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
        #max_key = max(self.menu_items, key=int)
        #self.back_option_key = str(int(max_key) + 1)
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


class DocTransactionWizard:
    """CLI wizard for initiate new document transactions / do a task /update a task."""

    def __init__(self, wallet, crypto_helper, network_interface, isInitial = False):
        self.wallet = wallet
        self.crypto_helper = crypto_helper
        self.network_interface = network_interface
        self.isInitial = isInitial
        """
        :param isInitial: set isInitial to true for initial transaction
        """

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
    def __validate_payload_attribute_input(usr_input):
        if len(usr_input) > 0:
            return True
        else:
            return False

    @staticmethod
    def __validate_incharge_input(usr_input):
        if len(usr_input) > 0:
            return True
        else:
            return False

    @staticmethod
    def __validate_next_incharge_input(usr_input):
        if len(usr_input) > 0:
            return True
        else:
            return False

    @staticmethod
    def __validate_string_zero_length(usr_input):
        if len(usr_input) > 0:
            return False
        else:
            return True

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
        usr_input = input('Please type a receiver address: ')
        return str(usr_input)

    @staticmethod
    def __ask_for_incharge():
        usr_input = input('Please type in_charge process ID: ')
        return str(usr_input)

    @staticmethod
    def __ask_for_next_incharge():
        usr_input = input('Please type next in_charge process ID: ')
        return str(usr_input)

    @staticmethod
    def __ask_for_payload_attribute():
        usr_input = input('Please type a payload attribute name: ')
        return str(usr_input)

    @staticmethod
    def __ask_for_payload():
        usr_input = input('Please type a payload (for boolean, please type true/false): ')
        return str(usr_input)

    @staticmethod
    def __ask_for_process_owner():
        usr_input = input('Please type a process owner (in charge) (empty input to finish the process owner input):')
        return str(usr_input)

    @staticmethod
    def __ask_for_process_receiver(pid_inCharge):
        print('Please type the next in charge for the pid ', pid_inCharge,  '(empty input to go to next process):')
        usr_input = input()
        return str(usr_input)

    @staticmethod
    def __ask_for_permission(data):
        print('Please type a pid permitted to change the data "', data, '"')
        print('empty input to go to next data field')
        usr_input = input()
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
            chosen_incharge = self.__ask_for_incharge()
            chosen_next_incharge = self.__ask_for_next_incharge()

            while not ((self.__validate_incharge_input(chosen_incharge))
                        & (self.__validate_next_incharge_input(chosen_next_incharge)) ):
                # clear_screen()
                print('Invalid input! Please choose a correct incharge and next incharge!')
                print(u'Sender: ' + str(chosen_key))
                print(u'Receiver: ' + str(chosen_receiver))
                chosen_incharge = self.__ask_for_incharge()
                chosen_next_incharge = self.__ask_for_next_incharge()
                print()

            if self.isInitial == False:
                chosen_payload_attribute = self.__ask_for_payload_attribute()
                chosen_payload = self.__ask_for_payload()
                while not ((self.__validate_payload_attribute_input(chosen_payload_attribute)) & (self.__validate_payload_input(chosen_payload))):
                    # clear_screen()
                    print('Invalid input! Please choose a correct attribute and payload!')
                    print(u'Sender: ' + str(chosen_key))
                    print(u'Receiver: ' + str(chosen_receiver))
                    chosen_payload_attribute = self.__ask_for_payload_attribute()
                    chosen_payload = self.__ask_for_payload()
                    print()

            if self.isInitial == True:
                """ask for document data"""
                payload_json = {}
                isPayloadFinish = False

                while isPayloadFinish == False:
                    chosen_payload_attribute = self.__ask_for_payload_attribute()
                    isPayloadFinish = self.__validate_string_zero_length(chosen_payload_attribute)
                    if isPayloadFinish == True:
                        break
                    chosen_payload = self.__ask_for_payload()
                    isPayloadFinish = self.__validate_string_zero_length(chosen_payload)
                    if isPayloadFinish == True:
                        break

                    payload_json[chosen_payload_attribute] = chosen_payload
                    clear_screen()
                    print('new attribute added:')
                    print(payload_json)
                    print()

                clear_screen()

                """ask for processes"""
                process_json = {}
                process_receiver = []
                isProcessFinish = False

                processOwner = ''
                while processOwner == '':
                    processOwner = self.__ask_for_process_owner()

                """add receiver to process receiver array"""
                isReceiverArrayFinish = False
                while (isReceiverArrayFinish == False or len(process_receiver) == 0):
                    receiver = ''
                    receiver = self.__ask_for_process_receiver(processOwner)
                    isReceiverArrayFinish = self.__validate_string_zero_length(receiver)
                    if (receiver != ''):
                        process_receiver.append(receiver)
                        process_json[processOwner] = process_receiver
                        print("current processes: ", process_json)
                        print()

                process_json[processOwner] = process_receiver

                print()
                print("current processes: ", process_json)
                print("finish? ")
                isFinish = input('y/n ')
                while isFinish != 'y' and isFinish != 'n':
                    isFinish = input("y/n")

                if isFinish == 'y':
                    isProcessFinish = True
                elif isFinish == 'n':
                    isProcessFinish = False

                #TODO try a better BFS tree implementation
                while isProcessFinish == False:
                    keys = [k for k in process_json]
                    d = process_json.copy()
                    noReceiverList = []

                    for key in d:
                        for v in d[key]:
                            if (v not in d) and (v not in noReceiverList):
                                process_receiver = []
                                """add receiver to process receiver array"""
                                isReceiverFinish = False
                                while (isReceiverFinish == False):
                                    receiver = ''
                                    receiver = self.__ask_for_process_receiver(v)
                                    isReceiverFinish = self.__validate_string_zero_length(receiver)
                                    if receiver == '':
                                        noReceiverList.append(v)
                                    if (receiver != ''):
                                        newOwner = v
                                        process_receiver.append(receiver)

                                    if process_receiver != []:
                                        process_json[newOwner] = process_receiver
                                        print("current processes: ", process_json)

                    print()
                    print("current processes: ", process_json)
                    print("finish? ")
                    isFinish = input('y/n ')
                    while isFinish != 'y' and isFinish != 'n':
                        isFinish = input("y/n")

                    if isFinish == 'y':
                        isProcessFinish = True
                    elif isFinish == 'n':
                        isProcessFinish = False

                clear_screen()

                """ask for permission"""
                permissionData_json = {}

                for key in payload_json:
                    isPermissionFinish = False
                    permission_pid = []
                    pid = ''
                    while isPermissionFinish == False:
                        pid = ''
                        pid = self.__ask_for_permission(key)
                        isPermissionFinish = self.__validate_string_zero_length(pid)
                        while (isPermissionFinish == False and (pid not in process_json)):
                            if pid != '':
                                print('the pid you enter is not contained in the processes!')
                                print()
                            pid = ''
                            print('your processes: ', process_json)
                            print()
                            pid = self.__ask_for_permission(key)
                            isPermissionFinish = self.__validate_string_zero_length(pid)

                        if pid != '':
                            permission_pid.append(pid)
                        if permission_pid != []:
                            permissionData_json[key] = permission_pid
                            print('your current permissions: ', permissionData_json)
                            print()
                    permissionData_json[key] = permission_pid

                clear_screen()

            # Create transaction Object and send to network
            private_key = wallet_list[int(chosen_key) - 1][2]
            public_key = wallet_list[int(chosen_key) - 1][1]

            if self.isInitial == False:
                transaction_json = {
                    "receiver": public_key,
                    "sender": private_key,
                    "signature": None,
                    "payload": {
                        "workflow-id": "0",
                        "document": {
                            chosen_payload_attribute: chosen_payload
                        },
                        "in_charge": chosen_incharge,
                        "next_in_charge": chosen_next_incharge,
                    }
                }

            elif self.isInitial == True:
                transaction_json = {
                    "receiver": public_key,
                    "sender": private_key,
                    "signature": None,
                    "payload": {
                        "workflow-id":"0",
                        "document": {

                        },
                        "in_charge": chosen_incharge,
                        "next_in_charge": chosen_next_incharge,
                        "processes":{

                        },
                        "permissions":{

                        }
                    }
                }
                transaction_json["payload"]["document"] = payload_json
                transaction_json["payload"]["processes"] = process_json
                transaction_json["payload"]["permissions"] = permissionData_json

            new_transaction = TaskTransaction.from_json(json.dumps(transaction_json))
            new_transaction.sign_transaction(self.crypto_helper, private_key)
            transaction_hash = self.crypto_helper.hash(json.dumps(transaction_json))
            if self.isInitial == False:
                self.network_interface.sendTransaction(new_transaction, 2) # 2 for TaskTransaction
            elif self.isInitial == True:
                self.network_interface.sendTransaction(new_transaction, 1) # 1 for WorkFlowTransaction

            print('Transaction successfully created!')
            print()
            print(u'Sender: ' + public_key)
            print(u'Receiver: ' + str(chosen_receiver))
            print("workflow-id: ", transaction_json["payload"]["workflow-id"])
            if self.isInitial == False:
                print(u'Payload key value: ' + str(chosen_payload_attribute), " : ", str(chosen_payload))
            print(u'Hash: ' + str(transaction_hash))
            if self.isInitial == True:
                print("transaction data: ", transaction_json["payload"]["document"])
                print("processes: ", transaction_json["payload"]["processes"])
                print("permissions: ", transaction_json["payload"]["permissions"])
            print()

        # case: wallet is empty
        else:
            print(u'Wallet does not contain any keys! Please create one first!')

        input('Press any key to go back to the main menu!')

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
            '2': ('Create Initial Transaction', self.__do_workflow, []),
            '3': ('doTask', self.__do_task, []),
            '4': ('Check Tasks', self.__check_tasks, [])
        }, 'Please select a value: ', 'Exit DocumentFlow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def __do_task(self):
        """Ask for all important information to create a new subsequent transaction/task and sends it to the network."""
        do_task_wizard = DocTransactionWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface)
        do_task_wizard.show()

    def __do_workflow(self):
        """Ask for all important information to create a new initial transaction/workflow and sends it to the network."""
        do_workflow_wizard = DocTransactionWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface,
                                               True)
        do_workflow_wizard.show()

    def __check_tasks(self):
        clear_screen()

        public_key = input('Please enter a pid: ')

        transactions = self.network_interface.requestAllTransactions()

        transaction_exist = False
        clear_screen()

        for transaction in transactions:
            #payloadArray = transaction.payload:
            #print(transaction.payload)
            if 'next_in_charge' in transaction.payload:
                dict = transaction.payload
                if dict['next_in_charge'] == public_key:
                    transaction_exist = True
                    print("it match")
                    print(transaction.payload)
                    #transaction.print()
                    print()

        if transaction_exist == False:
            print('Transaction does not exist')
        # wait for any input before returning to menu
        input('Press enter to continue...')


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
