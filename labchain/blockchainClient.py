import os
import pickle
import codecs
import json
from collections import OrderedDict

from labchain.network.networking import TransactionDoesNotExistException, BlockDoesNotExistException
from labchain.datastructure.transaction import Transaction, Transaction_Types
from labchain.datastructure.smartContract import SmartContract

LABCHAIN_LOGO = """
          .(##%*
         ,(%########((#/.                                                                                                         ..
        ,###(((###%(##(#####((#*              ....                      ...                         ...                          ....
       .#(((########((####%#######%((##*      ....                      ...                         ...                           ..
      ,(#(((%######(#######%#%#####(((###     ....           ....       ...   ...          ....     ...   ..          ....                    ...
     ,/##########((#####(((%############(     ....        ..........    ............    .........   ...........    ..........    ....   ...........
     ,(###(/#(/(########(((#####(#(#####(     ....               ...    ....    ....   ....         ....    ...           ....   ....   ....    ....
      /###########/(#((#########(((%#(###     ....          .........   ...      ....  ...          ...     ...       ........   ....   ....     ...
      /(##################((#(/#####(##(      ....       .....   ....   ...      ...   ...          ...     ...    ....   ....   ....   ....     ...
           .((/##################((#(#(       ....       ....    ....   ....    ....   ....     .   ...     ...   ....    ....   ....   ....     ...
                   .#(/############(((        ..........  ...........   ...........     .........   ...     ...    ...........   ....   ....     ...
                           *#/(####(/
                                  .#
"""

LABCHAIN_LOGO_LIST = LABCHAIN_LOGO.splitlines()


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
        max_key = max(self.menu_items, key=int)
        self.back_option_key = str(int(max_key) + 1)
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

    def __validate_sender_input(self, usr_input, length):
        try:
            int_usr_input = int(usr_input)
        except ValueError:
            return False

        if int_usr_input != 0 and int_usr_input <= length:
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
    def __ask_for_tx_type(tx_types_enum):
        print(u'Please select a transaction type: ')
        print()
        for key, value in tx_types_enum.items():
            print(str(key) + ':\t' + value)
        print()
        user_input = input('Please choose a transaction type (by number) or press enter to return: ')
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
            chosen_key = ''

            # ask for valid sender input in a loop
            while not self.__validate_sender_input(chosen_key, len(self.wallet)):
                chosen_key = self.__ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            # ask for valid transaction type input in a loop
            clear_screen()
            txTypes = Transaction_Types()
            tx_types_enum = {'1': txTypes.normal_transaction,
                            '2': txTypes.contract_creation,
                            '3': txTypes.method_call,
                            '4': txTypes.contract_termination,
                            '5': txTypes.contract_restoration}
            chosen_txType_index = ''
            while not self.__validate_sender_input(chosen_txType_index, len(tx_types_enum)):
                chosen_txType_index = self.__ask_for_tx_type(tx_types_enum)
                if chosen_txType_index == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()
            chosen_txType = tx_types_enum[chosen_txType_index]

            clear_screen()
            print(u'Sender: ' + str(chosen_key))
            print(u'Transaction Type: ' + chosen_txType) 

            # Handle the transaction depending on it's type
            if(chosen_txType == txTypes.normal_transaction):
                chosen_receiver, chosen_payload = self.handle_normal_transaction(chosen_key)
                chosen_txType = 'Normal Transaction'
            if(chosen_txType == txTypes.contract_creation):
                chosen_receiver, chosen_payload = self.handle_contract_creation()
                chosen_txType = 'Contract Creation'
            if(chosen_txType == txTypes.method_call):
                chosen_receiver, chosen_payload = self.handle_method_call(chosen_key)
                chosen_txType = 'Method Call'
            if(chosen_txType == txTypes.contract_termination):
                chosen_receiver, chosen_payload = self.handle_contract_termination()
                chosen_txType = 'Contract Termination'
            if(chosen_txType == txTypes.contract_restoration):
                chosen_receiver, chosen_payload = self.handle_contract_restoration()
                chosen_txType = 'Contract Restoration'

            clear_screen()
            # Create transaction Object and send to network
            private_key = wallet_list[int(chosen_key) - 1][2]
            public_key = wallet_list[int(chosen_key) - 1][1]

            #new_transaction = Transaction(str(public_key), str(chosen_receiver), str(chosen_payload), str(chosen_txType))
            new_transaction = Transaction(sender=str(public_key), receiver=str(chosen_receiver), payload=str(chosen_payload), transaction_type=str(chosen_txType))
            new_transaction.sign_transaction(self.crypto_helper, private_key)
            transaction_hash = self.crypto_helper.hash(new_transaction.get_json())

            self.network_interface.sendTransaction(new_transaction)

            print('Transaction successfully created!')
            print()
            print(u'Sender: ' + public_key)
            print(u'Transaction Type: ' + chosen_txType)
            print(u'Receiver: ' + chosen_receiver)
            print(u'Payload: ' + str(chosen_payload))
            print(u'Hash: ' + str(transaction_hash))
            print()

        # case: wallet is empty
        else:
            print(u'Wallet does not contain any keys! Please create one first!')

        input('Press any key to go back to the main menu!')


    def handle_normal_transaction(self, chosen_key):
        chosen_receiver = self.__ask_for_receiver()
        chosen_txType = Transaction_Types().normal_transaction
        while not self.__validate_receiver_input(chosen_receiver):
            clear_screen()
            print('Invalid input! Please choose a correct receiver!')
            print(u'Sender: ' + str(chosen_key))
            print(u'Transaction Type: ' + chosen_txType)
            chosen_receiver = self.__ask_for_receiver()
            print()

        print(u'Receiver: ' + str(chosen_receiver))
        chosen_payload = self.__ask_for_payload()
        while not self.__validate_payload_input(chosen_payload):
            clear_screen()
            print('Invalid input! Please choose a correct payload!')
            print(u'Sender: ' + str(chosen_key))
            print(u'Transaction Type: ' + str(chosen_txType))
            print(u'Receiver: ' + str(chosen_receiver))
            chosen_payload = self.__ask_for_payload()
            print()

        return chosen_receiver, chosen_payload


    def handle_contract_creation(self):
        chosen_receiver = ''
        payload = {"contractCode":'', "arguments":""}
        pathToContract = "/Users/joseminguez/Desktop/Contracts/PiggyBankContract/contract.py"
        #pathToContract = input('Please enter the path to your contract: ').replace(' ', '')
        pickledContract = None
        with open(pathToContract, 'r') as file:
            pickledContract = pickle.dumps(file.read())
        payload["contractCode"] = codecs.encode(pickle.dumps(pickledContract), "base64").decode()
        print('Contract successfully imported.')
        arguments = input("Please enter the arguments for the contract's constructor in dict format: ")
        payload['arguments'] = json.loads(arguments)
        chosen_payload = payload

        return chosen_receiver, chosen_payload
    

    def handle_method_call(self, chosen_key):
        chosen_receiver = self.__ask_for_receiver()
        chosen_txType = Transaction_Types().method_call
        while not self.__validate_receiver_input(chosen_receiver):
            clear_screen()
            print('Invalid input! Please choose a correct receiver!')
            print(u'Sender: ' + str(chosen_key))
            print(u'Transaction Type: ' + str(chosen_txType))
            chosen_receiver = self.__ask_for_receiver()
            print()

        print(u'Receiver: ' + str(chosen_receiver))
        chosen_payload = {'methods':[]}
        methods = []
        methodName = input("Please enter name of the method you want to call on this contract: ")
        arguments = json.loads(input("Please enter arguments of the method in dict format (leave empty if no arguments): "))
        moreArguments = True
        while moreArguments:
            methodToCall = {'methodName':methodName, 'arguments':arguments}
            methods.append(methodToCall)
            methodName = input(("Please enter name of another method you want to call on this contract "
                            + "(leave empty if you do not want to call any other methods): "))
            if methodName == '':
                moreArguments = False
                break
            arguments = input("Please enter arguments of the method in dict format (leave empty if no arguments): ")
        chosen_payload['methods'] = methods

        return chosen_receiver, chosen_payload


    def handle_contract_termination(self):
        chosen_receiver = self.__ask_for_receiver()
        chosen_payload = {}
        return chosen_receiver, chosen_payload


    def handle_contract_restoration(self):
        chosen_receiver = self.__ask_for_receiver()
        payload = {"contractCode":'', "arguments":""}
        #pathToContract = "/Users/joseminguez/Desktop/Contracts/PiggyBankContract/contract.py"
        pathToContract = input('Please enter the path to your contract: ').replace(' ', '')
        pickledContract = None
        with open(pathToContract, 'r') as file:
            pickledContract = pickle.dumps(file.read())
        payload["contractCode"] = codecs.encode(pickle.dumps(pickledContract), "base64").decode()
        print('Contract successfully imported.')
        arguments = input("Please enter the arguments for the contract's constructor in dict format: ")
        payload['arguments'] = json.loads(arguments)
        chosen_payload = payload

        return chosen_receiver, chosen_payload


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
        self.main_menu = Menu(LABCHAIN_LOGO_LIST + ['Main menu'], {
            '1': ('Manage Wallet', self.manage_wallet_menu.show, []),
            '2': ('Create Transaction', self.__create_transaction, []),
            '3': ('Load Block', self.load_block_menu.show, []),
            '4': ('Load Transaction', self.__load_transaction, []),
            '5': ('Load Contract', self.__load_contract, []),
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
    
    def __create_contract(self):
        """Ask for all important information to create a new contract transaction and sends it to the network."""

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
                               'Please select a key to delete: ', 'Exit without deleting any addresses', True)
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

    def __load_transaction(self):
        """Prompt the user for a transaction hash and display the transaction details."""
        clear_screen()
        transaction_hash = input('Please enter a transaction hash: ')
        try:
            transaction, block_hash = self.network_interface.requestTransaction(transaction_hash)
        except TransactionDoesNotExistException:
            transaction = None

        clear_screen()
        if not transaction:
            print('Transaction does not exist')
        else:
            print('Sender ID: {}'.format(transaction.sender))
            print('Receiver ID: {}'.format(transaction.receiver))
            print('Payload: {}'.format(transaction.payload))
            print('Signature: {}'.format(transaction.signature))
            print('Block Hash: {}'.format(block_hash))
        print()
        # wait for any input before returning to menu
        input('Press enter to continue...')

    def __load_contract(self):
        """Prompt the user for a contract's hash and display the contract's details."""
        clear_screen()
        contract_address = input('Please enter a contract\'s address: ')        
        
        try:
            contract = self.network_interface.requestContract(contract_address)
            if contract['terminated']:
                print("This contract has been terminated.")
                print()
                # wait for any input before returning to menu
                input('Press enter to continue...')
                return
            contract_state = self.network_interface.requestContractState(contract_address)
            contract_state_encoded = contract['state']
            contract_code = contract['code']
            contract_address = contract['addresses'][-1]
        except:
            print("No contract was found")
            print()
            # wait for any input before returning to menu
            input('Press enter to continue...')
            return
        contract_options =   {  '1': 'Get the state of the contract',
                                '2': 'Get the callable methods from the contract',
                                '3': 'Get the code of the contract'}
        chosen_contract_option = ''
        while not self.__validate_sender_input(chosen_contract_option, len(contract_options)):
            chosen_contract_option = self.__ask_for_contract_interaction(contract_options)
            if chosen_contract_option == '1':
                print()
                print('Contract\'s state:')
                print(type(contract_state))
                print(contract_state)
                for key, value in contract_state.items():
                    print('\t' + str(key) + ": " + str(value))
                print()
                input('Press enter to continue...')
            if chosen_contract_option == '2':
                print()
                print('Contract\'s methods:\n' )
                methods = self.network_interface.requestMethods(contract_state_encoded, contract_address)
                for key, value in methods.items():
                    print('\t' + str(key) + ': ' + str(value))
                print()
                input('Press enter to continue...')
            if chosen_contract_option == '3':
                print('Contract\'s code:\n')
                decoded_code = pickle.loads(codecs.decode(contract_code.encode(), "base64"))
                print(str(pickle.loads(decoded_code)))
                print()
                input('Press enter to continue...')
            if chosen_contract_option == '':
                return
            print('Invalid input! Please choose a correct index!')
            print()

    def __validate_sender_input(self, usr_input, length):
        try:
            int_usr_input = int(usr_input)
        except ValueError:
            return False

        if int_usr_input != 0 and int_usr_input <= length:
            return True
        else:
            return False
        
    @staticmethod
    def __ask_for_contract_interaction(contract_options):
        print(u'Please select one of the following options for interacting with the contract: ')
        print()
        for key, value in contract_options.items():
            print(str(key) + ':\t' + value)
        print()
        user_input = input('Please choose an option (by number) or press enter to return: ')
        return user_input