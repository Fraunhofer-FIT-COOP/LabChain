import os
import json

from labchain.util.Menu import Menu
from labchain.blockchainClient import TransactionWizard
from labchain.util.TransactionFactory import TransactionFactory
from labchain.workflow.taskTransaction import TaskTransaction, WorkflowTransaction


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class TaskTransactionWizard(TransactionWizard):

    def __init__(self, wallet, crypto_helper, network_interface):
        super().__init__(wallet, crypto_helper, network_interface)

    @staticmethod
    def validate_wf_id_input(chosen_wf_id, wf_ids):
        if chosen_wf_id in wf_ids:
            return True
        else:
            return False

    @staticmethod
    def ask_for_task_id(tasks):
        if len(tasks) == 0:
            print(u'There is no task received.')
            input('Press any key to go back to the main menu!')
            return ''

        print(u'Current workflows that are waiting with the following ids: ')
        for counter, key in enumerate(tasks, 1):
            print()
            print(u'\t' + str(key))
            print()

        user_input = input('Please choose a workflow id to work on or press enter to return: ')
        return user_input

    def ask_for_receiver(self, receiver_list):
        print(u'Possible receivers listed: ')
        for tuple in list(enumerate(receiver_list)):
            print()
            print(str(tuple[0]+1) + u':\t' + str(tuple[1].split('_')[0]))
            print()

        user_input = input('Please choose a receiver account (by number) or press enter to return: ')
        return str(int(user_input) - 1)

    def ask_for_data(self, modifiable):
        print(u'Please enter values for:')
        data = dict()
        for data_key in modifiable:
            print()
            data[data_key] = input(str(data_key) + u':\t')
        return data


    def validate_receiver_input(self, usr_input, receivers_len):
        try:
            int_usr_input = int(usr_input)
        except ValueError:
            return False
        if int_usr_input <= receivers_len:
            return True
        else:
            return False

    def check_tasks(self, public_key):
        received = self.network_interface.search_transaction_from_receiver(public_key)
        send = self.network_interface.search_transaction_from_sender(public_key)
        received_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in received if
                                     'workflow_id' in t.payload]
        send_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in send if
                                 'workflow_id' in t.payload]
        send_task_transaction = [t for t in send_task_transaction if t.type == '2']
        received_task_transaction_dict = {self.crypto_helper.hash(t.get_json()): t for t in received_task_transaction}
        send_task_transaction_dict = {t.previous_transaction: t for t in send_task_transaction}
        diff = {k: received_task_transaction_dict[k] for k in set(received_task_transaction_dict)
                - set(send_task_transaction_dict)}
        return [diff[k] for k in diff]


    def show(self):
        """Start the wizard."""
        clear_screen()

        # convert dict to an ordered list
        # this needs to be done to get an ordered list that does not change
        # at runtime of the function
        wallet_list = self.wallet_to_list()

        # check if wallet contains any keys
        # case: wallet not empty
        if not len(self.wallet) == 0:

            chosen_key = self.ask_for_key_from_wallet(wallet_list)
            if chosen_key == '':
                return

            # ask for valid sender input in a loop
            while not self.validate_sender_input(chosen_key):
                chosen_key = self.ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print(u'Sender: ' + str(chosen_key))


            private_key = wallet_list[int(chosen_key) - 1][2]
            public_key = wallet_list[int(chosen_key) - 1][1]

            tasks = self.check_tasks(public_key)
            workflow_ids = [task.payload['workflow_id'] for task in tasks]
            chosen_wf_id = self.ask_for_task_id(workflow_ids)
            if chosen_wf_id == '':
                return

            # ask for valid sender input in a loop
            while not self.validate_wf_id_input(chosen_wf_id, workflow_ids):
                clear_screen()
                print('Invalid input! Please choose a correct workflow id!')
                print()
                chosen_wf_id = self.ask_for_task_id(workflow_ids)
                if chosen_wf_id == '':
                    return

            clear_screen()
            print(u'Sender: ' + str(chosen_key))
            print(u'Chosen workflow id: ' + str(chosen_wf_id))

            task = [element for element in tasks if element.payload['workflow_id'] == chosen_wf_id][0]
            task_hash = self.crypto_helper.hash(task.get_json())
            prev_transaction = self.network_interface.requestTransaction(task_hash)[0]
            if type(task) == WorkflowTransaction:
                workflow_transaction_hash = task_hash
                workflow_transaction = prev_transaction
            else:
                workflow_transaction_hash = prev_transaction.payload["workflow_transaction"]
                workflow_transaction = self.network_interface.requestTransaction(workflow_transaction_hash)[0]

            in_charge = prev_transaction.payload['in_charge']
            if in_charge in workflow_transaction.payload['processes'].keys():
                next_in_charge_list = workflow_transaction.payload['processes'][in_charge]
            else:
                input("End of workflow. Please press any key to return!")
                return


            receiver_index = self.ask_for_receiver(next_in_charge_list)
            if receiver_index == '':
                return
            while not self.validate_receiver_input(receiver_index, len(next_in_charge_list)):
                # clear_screen()
                print('Invalid input! Please choose a correct receiver!')
                print(u'Sender: ' + str(chosen_key))
                print(u'Chosen workflow id: ' + str(chosen_wf_id))
                receiver_index = self.ask_for_receiver(next_in_charge_list)
                if receiver_index == '':
                    return
                print()
            next_in_charge = next_in_charge_list[int(receiver_index)]
            chosen_receiver = next_in_charge.split('_')[0]

            clear_screen()
            print(u'Sender: ' + str(chosen_key))
            print(u'Chosen workflow id: ' + str(chosen_wf_id))
            print(u'Receiver: ' + str(chosen_receiver))

            attributes = workflow_transaction.payload['permissions'].keys()
            modifiable = list()
            for attr in attributes:
                allowed_list = workflow_transaction.payload['permissions'][attr]
                for allowed in allowed_list:
                    if allowed == in_charge:
                        modifiable.append(attr)

            if len(modifiable) == 0:
                print(u'You are not permissioned to modify any data.')
                input('Press any key to send the transaction!')
                data = dict()
            else:
                data = self.ask_for_data(modifiable)

            document = data

            chosen_payload = dict(workflow_id=chosen_wf_id, document=document,
                                  in_charge=next_in_charge, workflow_transaction=workflow_transaction_hash,
                                  previous_transaction=task_hash)

            new_transaction = TransactionFactory.create_transaction(dict(sender=public_key,
                                                                     receiver=chosen_receiver,
                                                                     payload=chosen_payload,
                                                                     signature=''))
            new_transaction.sign_transaction(self.crypto_helper, private_key)
            transaction_hash = self.crypto_helper.hash(new_transaction.get_json())

            self.network_interface.sendTransaction(new_transaction)

            print('Transaction successfully created!')
            print()
            print(u'Sender: ' + wallet_list[int(chosen_key) - 1][2])
            print(u'Receiver: ' + str(chosen_receiver))
            print(u'Payload: ' + str(chosen_payload))
            print(u'Hash: ' + str(transaction_hash))
            print()

        # case: wallet is empty
        else:
            print(u'Wallet does not contain any keys! Please create one first!')

        input('Press any key to go back to the main menu!')

class WorkflowTransactionWizard(TransactionWizard):

    def __init__(self, wallet, crypto_helper, network_interface):
        super().__init__(wallet, crypto_helper, network_interface)
        self.my_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources'))

    def get_workflow_list(self, directory):
        path_list = list()
        for file in os.listdir(self.my_dir):
            if file.endswith(".json"):
                path_list.append(file)
        return path_list

    @staticmethod
    def validate_workflow_input(usr_input, workflow_resource_len):
        try:
            int_usr_input = int(usr_input)
        except ValueError:
            return False

        if int_usr_input != 0 and int_usr_input <= workflow_resource_len:
            return True
        else:
            return False

    @staticmethod
    def ask_for_workflow_id():
        usr_input = input('Please type in a workflow id: ')
        return str(usr_input)

    @staticmethod
    def ask_for_workflow(workflow_list):
        print(u'Current workflow files in resources: ')
        for counter, key in enumerate(workflow_list, 1):
            print()
            print(u'\t' + str(counter) + ': ' + str(key))
            print()

        user_input = input('Please choose a workflow file (by number) or press enter to return: ')
        return user_input

    def show(self):
        """Start the wizard."""
        clear_screen()

        # convert dict to an ordered list
        # this needs to be done to get an ordered list that does not change
        # at runtime of the function
        wallet_list = self.wallet_to_list()
        workflow_list = self.get_workflow_list(self.my_dir)

        if len(workflow_list) == 0:
            #   case: workflow resources are empty
            print(u'There is no workflow file in resources! Please create one first!')
        elif len(self.wallet) == 0:
            #   case: wallet is empty
            print(u'Wallet does not contain any keys! Please create one first!')
        else:
            chosen_workflow = self.ask_for_workflow(workflow_list)
            if chosen_workflow == '':
                return
            # ask for valid workflow input in a loop
            while not self.validate_workflow_input(chosen_workflow, len(workflow_list)):
                chosen_workflow = self.ask_for_workflow(workflow_list)
                if chosen_workflow == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))

            chosen_key = self.ask_for_key_from_wallet(wallet_list)
            if chosen_key == '':
                return

            # ask for valid sender input in a loop
            while not self.validate_sender_input(chosen_key):
                chosen_key = self.ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
            print(u'Sender: ' + str(chosen_key))
            chosen_receiver = self.ask_for_receiver()

            while not self.validate_receiver_input(chosen_receiver):
                # clear_screen()
                print('Invalid input! Please choose a correct receiver!')
                print(u'Sender: ' + str(chosen_key))
                chosen_receiver = self.ask_for_receiver()
                print()

            clear_screen()
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
            print(u'Sender: ' + str(chosen_key))
            print(u'Receiver: ' + str(chosen_receiver))

            # Create transaction object and send to network
            private_key = wallet_list[int(chosen_key) - 1][2]
            public_key = wallet_list[int(chosen_key) - 1][1]

            chosen_workflow_id = self.ask_for_workflow_id()
            path = os.path.join(self.my_dir, str(workflow_list[int(chosen_workflow) - 1]))
            with open(path) as f:
                chosen_payload = json.load(f)
            chosen_payload["workflow_id"] = chosen_workflow_id

            transaction = TransactionFactory.create_transaction(dict(sender=public_key,
                                                                     receiver=chosen_receiver,
                                                                     payload=chosen_payload,
                                                                     signature=''))
            transaction.sign_transaction(self.crypto_helper, private_key)
            self.network_interface.sendTransaction(transaction)
            transaction_hash = self.crypto_helper.hash(transaction.get_json())
            print('Workflow successfully created!')
            print()
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
            print(u'Sender: ' + wallet_list[int(chosen_key) - 1][2])
            print(u'Receiver: ' + str(chosen_receiver))
            print(u'Payload: ' + str(chosen_payload))
            print(u'Hash: ' + str(transaction_hash))
            print()
        input('Press any key to go back to the main menu!')

class WorkflowClient:

    def __init__(self, wallet, network_interface, crypto_helper):
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.wallet = wallet
        self.workflow_transaction_wizard = WorkflowTransactionWizard(self.wallet,
                                               self.crypto_helper,
                                               self.network_interface)
        self.task_transaction_wizard = TaskTransactionWizard(self.wallet,
                                                                     self.crypto_helper,
                                                                     self.network_interface)
        self.main_menu = Menu(['Main menu'], {
            '1': ('Create workflow transaction', self.send_workflow_transaction, []),
            '2': ('Send transaction', self.send_task_transaction, [])
        }, 'Please select a value: ', 'Exit Workflow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def send_workflow_transaction(self):
        self.workflow_transaction_wizard.show()

    def send_task_transaction(self):
        self.task_transaction_wizard.show()

    def show_completed_workflows(self):
        #TODO
        pass
