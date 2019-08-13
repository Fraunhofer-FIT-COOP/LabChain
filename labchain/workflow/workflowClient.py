import os
import json
import pprint

from labchain.util.Menu import Menu
from labchain.blockchainClient import TransactionWizard
from labchain.util.TransactionFactory import TransactionFactory
from labchain.workflow.taskTransaction import TaskTransaction, WorkflowTransaction

RESOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources'))


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class TaskTransactionWizard(TransactionWizard):

    def __init__(self, wallet, crypto_helper, network_interface):
        super().__init__(wallet, crypto_helper, network_interface)
        self.my_dir = RESOURCE_DIR

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
        received_workflow_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in received if
                                     'processes' in t.payload]
        received_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in received if
                                     'workflow_id' in t.payload and 'processes' not in t.payload]
        send_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in send if
                                 'workflow_id' in t.payload and 'processes' not in t.payload]

        send_task_transaction = self.rearrange_send_task_transactions(send_task_transaction)
        received_task_transaction = self.rearrange_received_task_transactions(received_task_transaction)
        received_task_transaction_dict = {self.crypto_helper.hash(t.get_json()): t for t in received_task_transaction}
        received_tx_dict = {**received_task_transaction_dict, **{self.crypto_helper.hash(t.get_json()): t for t in received_workflow_transaction}}
        send_task_transaction_dict = {t.previous_transaction: t for t in send_task_transaction}
        diff = {k: received_tx_dict[k] for k in set(received_tx_dict)
                - set(send_task_transaction_dict)}
        return [diff[k] for k in diff]

    @staticmethod
    def group_dict_by_wf_id(tx_list):
        grouped_dict_by_wf_id = dict()
        for tx in tx_list:
            key = tx.payload["workflow_transaction"]
            if key in grouped_dict_by_wf_id:
                grouped_dict_by_wf_id[key].append(tx)
            else:
                grouped_dict_by_wf_id[key] = list()
                grouped_dict_by_wf_id[key].append(tx)
        return grouped_dict_by_wf_id

    def rearrange_received_task_transactions(self, received_task_transaction):
        # TODO shows the workflow id twice if there's one split tx  and one linear waiting for OR split
        # TODO shows the split tx even if wf completed on other branch
        grouped_dict_by_wf_id = self.group_dict_by_wf_id(received_task_transaction)

        for workflow_tx in grouped_dict_by_wf_id:
            split_dict = WorkflowTransaction.from_json(self.network_interface.requestTransaction(workflow_tx)[0]
                                                       .get_json_with_signature()).splits
            # just a regular linear wf -> continue
            if len(split_dict.keys()) == 0:
                continue
            # wf has splits
            process_dict = WorkflowTransaction.from_json(self.network_interface.requestTransaction(workflow_tx)[0]
                                                         .get_json_with_signature()).processes
            for merge_type, merge_addr_list in split_dict.items():
                for addr in merge_addr_list:
                    split_addresses = [sender for sender, receiver_list in process_dict.items() if
                                       addr in receiver_list]
                    sent_split_txs = [tx for tx in grouped_dict_by_wf_id[workflow_tx] if tx.in_charge == addr]
                    if len(sent_split_txs) < len(split_addresses) and merge_type == "AND":
                        for tx in sent_split_txs:
                            received_task_transaction.remove(tx)
                    elif len(sent_split_txs) < len(split_addresses) and merge_type == "OR":
                        if len(sent_split_txs) > 1:
                            for sent_split_tx in sent_split_txs[1:]:
                                received_task_transaction.remove(sent_split_tx)
                        else:
                            continue
                    elif len(sent_split_txs) == len(split_addresses):
                        received_task_transaction.remove(sent_split_txs[0])
        return received_task_transaction

    def rearrange_send_task_transactions(self, send_task_transaction):
        grouped_dict_by_wf_id = self.group_dict_by_wf_id(send_task_transaction)

        for workflow_tx in grouped_dict_by_wf_id:
            split_dict = WorkflowTransaction.from_json(self.network_interface.requestTransaction(workflow_tx)[0]
                                           .get_json_with_signature()).splits

            # wf has splits
            process_dict = WorkflowTransaction.from_json(self.network_interface.requestTransaction(workflow_tx)[0]
                                                         .get_json_with_signature()).processes
            splits = [lists for lists in process_dict.values() if len(lists) > 1]
            # just a regular linear wf -> continue
            if len(split_dict.keys()) == 0 and not len(splits) > 0:
                continue

            next_in_charge_list = [tx.in_charge for tx in grouped_dict_by_wf_id[workflow_tx]]
            not_completed = list()
            for split_list in splits:
                for addr in split_list:
                    if addr not in next_in_charge_list:
                        not_completed.append(split_list)

            for split in not_completed:
                for addr in split:
                    if addr in next_in_charge_list:
                        send_task_transaction.remove([tx for tx in send_task_transaction if tx.in_charge == addr][0])
        return send_task_transaction


    def get_all_received_workflow_transactions(self, public_key):
        received = self.network_interface.search_transaction_from_receiver(public_key)
        received_workflow_transactions = [WorkflowTransaction.from_json(t.get_json_with_signature()).payload for t in received if
                                     'processes' in t.payload]
        return received_workflow_transactions

    def check_if_wf_ended(self, public_key, wf_id):
        received = self.network_interface.search_transaction_from_receiver(public_key)
        received_workflow_transactions = [TaskTransaction.from_json(t.get_json_with_signature()).payload["workflow_id"]==wf_id for t in received if
                                     'workflow_id' in t.payload]
        return True if True in received_workflow_transactions else False

    def get_workflow_status(self, workflow_payload):
        addrs = self.get_last_accounts(workflow_payload)
        result = True
        for addr in addrs:
            if not self.check_if_wf_ended(addr, workflow_payload["workflow_id"]):
                result = False
        return "Completed" if result else "In Progress"

    def get_last_accounts(self, workflow_payload):
        all_addresses = set([item.split('_')[0] for sublist in workflow_payload["processes"].values() for item in sublist])
        last_accounts = list()
        for addr in all_addresses:
            if addr not in [item.split('_')[0] for item in workflow_payload["processes"].keys()]:
                last_accounts.append(addr)
        return last_accounts

    def get_workflow_name(self, workflow_payload):
        for file in os.listdir(self.my_dir):
            with open(os.path.join(self.my_dir, file)) as f:
                wf_definition = json.load(f)
                document_cond = set(wf_definition["document"].keys())  == set(workflow_payload["document"].keys())
                permissions_cond = set(wf_definition["permissions"].keys())  == set(workflow_payload["permissions"].keys())
                split_cond = set(wf_definition["splits"].keys())  == set(workflow_payload["splits"].keys())
                if document_cond  and permissions_cond and split_cond:
                    return file

    def show_workflow_status(self):
        clear_screen()
        wallet_list = self.wallet_to_list()

        if not len(self.wallet) == 0:
            print("Please choose the account to see related workflows!")
            chosen_key = self.ask_for_key_from_wallet(wallet_list)
            if chosen_key == '':
                return

            while not self.validate_sender_input(chosen_key):
                print("Please choose the account to see related workflows!")
                chosen_key = self.ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()

            clear_screen()
            print(u'Account: ' + str(chosen_key))
            public_key = wallet_list[int(chosen_key) - 1][1]

            workflow_transactions = self.get_all_received_workflow_transactions(public_key)
            if len(workflow_transactions) == 0:
                print("You have not started any workflows!")
                input('Press any key to go back to the main menu!')
                return
            for (key, wf_tx) in enumerate(workflow_transactions):
                print()
                print(str(key+1) + u':  Workflow id: ' + str(wf_tx["workflow_id"] + '\t---->\t' +
                      self.get_workflow_name(wf_tx) + '\t---->\t' + self.get_workflow_status(wf_tx)))
                print()
            input('Press any key to go back to the main menu!')

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
        self.my_dir = RESOURCE_DIR
        self.pp = pprint.PrettyPrinter(indent=2)

    def get_workflow_list(self):
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
    def ask_for_key_from_wallet(wallet_list):
        print(u'Current keys in the wallet: ')
        for counter, key in enumerate(wallet_list, 1):
            print()
            print(str(counter) + u':\t' + str(key[0]))
            print()

        user_input = input('Please choose an account (by number) or press enter to return: ')
        return user_input

    @staticmethod
    def ask_for_workflow(workflow_list):
        print(u'Current workflow files in resources: ')
        for counter, key in enumerate(workflow_list, 1):
            print()
            print(u'\t' + str(counter) + ': ' + str(key))
            print()

        user_input = input('Please choose a workflow file (by number) or press enter to return: ')
        return user_input

    @staticmethod
    def get_all_entities_in_wf(workflow_template):
        task_entities = set()
        in_charge_entity = workflow_template["in_charge"].split("_")[0]
        for key, values in workflow_template["processes"].items():
            if in_charge_entity != key.split("_")[0]:
                task_entities.add(key.split("_")[0])
            for value in values:
                if in_charge_entity != value.split("_")[0]:
                    task_entities.add(value.split("_")[0])
        return in_charge_entity, task_entities

    def exchange_entities_with_pks(self, workflow_template, exchange_dict):
        workflow_str = json.dumps(workflow_template)
        for key, value in exchange_dict.items():
            workflow_str = workflow_str.replace(key, value)
        return json.loads(workflow_str)

    def show(self):
        """Start the wizard."""
        clear_screen()

        # convert dict to an ordered list
        # this needs to be done to get an ordered list that does not change
        # at runtime of the function
        wallet_list = self.wallet_to_list()
        workflow_list = self.get_workflow_list()

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

            path = os.path.join(self.my_dir, str(workflow_list[int(chosen_workflow) - 1]))
            with open(path) as f:
                chosen_payload = json.load(f)

            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
            self.pp.pprint(chosen_payload)
            print("-------------------------------------------------------------")
            print("Please enter a sender account.")
            chosen_sender = self.ask_for_key_from_wallet(wallet_list)
            if chosen_sender == '':
                return

            # ask for valid sender input in a loop
            while not self.validate_sender_input(chosen_sender):
                clear_screen()
                print('Invalid input! Please choose a correct index!')
                print()
                print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
                self.pp.pprint(chosen_payload)
                print("-------------------------------------------------------------")
                print("Please enter a sender account.")
                chosen_key = self.ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return

            clear_screen()
            sender_private_key = wallet_list[int(chosen_sender) - 1][2]
            sender_public_key = wallet_list[int(chosen_sender) - 1][1]

            in_charge_entity, task_entities = self.get_all_entities_in_wf(chosen_payload)
            exchange_dict = dict()
            exchange_dict[in_charge_entity] = sender_public_key

            for entity in task_entities:
                print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
                print(u'Sender: ' + str(wallet_list[int(chosen_sender) - 1][0]))
                print("-------------------------------------------------------------")
                print("Please enter an account for: ", entity)
                chosen_key = self.ask_for_key_from_wallet(wallet_list)
                if chosen_key == '':
                    return

                # ask for valid sender input in a loop
                while not self.validate_sender_input(chosen_key):
                    clear_screen()
                    print('Invalid input! Please choose a correct index!')
                    print()
                    print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
                    print(u'Sender: ' + str(wallet_list[int(chosen_sender) - 1][0]))
                    print("-------------------------------------------------------------")
                    print("Please enter an account for: ", entity)
                    chosen_key = self.ask_for_key_from_wallet(wallet_list)
                    if chosen_key == '':
                        return
                exchange_dict[entity] = wallet_list[int(chosen_key) - 1][1]
                clear_screen()

            chosen_payload = self.exchange_entities_with_pks(chosen_payload, exchange_dict)
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
            print(u'Your workflow data:')
            self.pp.pprint(chosen_payload)

            chosen_workflow_id = self.ask_for_workflow_id()
            #TODO add a check for workflow id
            chosen_payload["workflow_id"] = chosen_workflow_id

            transaction = TransactionFactory.create_transaction(dict(sender=sender_public_key,
                                                                     receiver=sender_public_key,
                                                                     payload=chosen_payload,
                                                                     signature=''))
            transaction.sign_transaction(self.crypto_helper, sender_private_key)
            self.network_interface.sendTransaction(transaction)
            transaction_hash = self.crypto_helper.hash(transaction.get_json())
            clear_screen()
            print('Workflow successfully created!')
            print()
            print(u'Workflow: ' + str(workflow_list[int(chosen_workflow) - 1]))
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
            '2': ('Send transaction', self.send_task_transaction, []),
            '3': ('Show workflow status', self.show_workflow_status, []),
        }, 'Please select a value: ', 'Exit Workflow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def send_workflow_transaction(self):
        self.workflow_transaction_wizard.show()

    def send_task_transaction(self):
        self.task_transaction_wizard.show()

    def show_workflow_status(self):
        self.task_transaction_wizard.show_workflow_status()
