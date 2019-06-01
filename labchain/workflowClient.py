import json
import os

from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.util.Menu import Menu
from labchain.util.TransactionFactory import TransactionFactory
from labchain.util.publicKeyNameMaping import PublicKeyNamesMapping


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class WorkflowClient:

    demo_workflow_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'demo-workflow.json'))

    def __init__(self, wallet, network_interface, crypto_helper):
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.main_menu = Menu(['Main menu'], {
            '1': ('Create workflow transaction',self.send_workflow_transaction,[]),
            '2': ('Send task transaction',self.send_task_transaction,[]),
            '3': ('Get transaction hash',self.get_transaction_hash,[])
        }, 'Please select a value: ', 'Exit Workflow Client')

    def main(self):
        self.read_workflow_json()
        """Entry point for the client console application."""
        self.main_menu.show()


    def send_workflow_transaction(self):
        transaction = TransactionFactory.create_transcation(self.workflow_json["workflow"])
        for k,v in  self.workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(self.crypto_helper,  v["private_key"])        
        print(self.crypto_helper.hash(transaction.get_json_without_signature()))
        self.network_interface.sendTransaction(transaction)

    def send_task_transaction(self):
        transactionName = input('which transaction (task1,task2,task3,invalid_task1)?')
        transaction = TransactionFactory.create_transcation(self.workflow_json[transactionName])
        for k,v in  self.workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(self.crypto_helper,  v["private_key"])
        print(self.crypto_helper.hash(transaction.get_json_without_signature()))
        self.network_interface.sendTransaction(transaction)

    def read_workflow_json(self):
        with open(self.demo_workflow_file_path, 'r') as file:
            self.workflow_json = json.load(file)[0]

    def get_transaction_hash(self):
        transaction = input('which workflow,task1,task2,task3,invalid_task1?')
        transaction = TransactionFactory.create_transcation(self.workflow_json[transaction])
        print(self.crypto_helper.hash(transaction.get_json_without_signature()))

        
        


