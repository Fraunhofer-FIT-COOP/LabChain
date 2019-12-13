import json
import os
from typing import List
from time import sleep
from multiprocessing import Process

from labchain.workflow.taskTransaction import TaskTransaction
from labchain.util.TransactionFactory import TransactionFactory


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


class Benchmarking:
    demo_workflow_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources/ThomasWorkflow.json'))

    def __init__(self, network_interface, crypto_helper):
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.read_workflow_json()
        self.wallet = self.workflow_json['wallet']

    # def check_for_open_tasks(self):
    #     wallet_dict = self.wallet_to_dict()
    #     if len(wallet_dict) > 0:
    #         wallet_id = self.ask_for_key(wallet_dict)
    #         wallet = wallet_dict[wallet_id]
    #         tasks = self.check_tasks(wallet[1])
    #         from ast import literal_eval
    #         for task in tasks:
    #             d = literal_eval(str(task))
    #             print('Sender Address:   {}'.format(d['sender']))
    #             print('Receiver Address: {}'.format(d['receiver']))
    #             print('Payload:          {}'.format(d['payload']))
    #             print('Signature:        {}'.format(d['signature']))
    #         input('Press any key to return: ')

    # def wallet_to_dict(self):
    #     wallet_dict_result = {}
    #     for key in sorted(self.wallet):
    #         pr = self.wallet[key]["private_key"]
    #         pu = self.wallet[key]["public_key"]
    #         wallet_dict_result[str(key)] = (pr, pu)
    #     return wallet_dict_result
    #
    # def check_tasks(self, public_key) -> List[TaskTransaction]:
    #     received = self.network_interface.search_transaction_from_receiver(public_key)
    #     send = self.network_interface.search_transaction_from_sender(public_key)
    #     received_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in received if
    #                                  'workflow_id' in t.payload]
    #     send_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in send if
    #                              'workflow_id' in t.payload]
    #     send_task_transaction = [t for t in send_task_transaction if t.type == '2']
    #     received_task_transaction_dict = {self.crypto_helper.hash(t.get_json()): t for t in received_task_transaction}
    #     send_task_transaction_dict = {t.previous_transaction: t for t in send_task_transaction}
    #     diff = {k: received_task_transaction_dict[k] for k in set(received_task_transaction_dict)
    #             - set(send_task_transaction_dict)}
    #     return [diff[k] for k in diff]

    def send_workflow_transaction(self):
        transaction = TransactionFactory.create_transcation(self.workflow_json["workflow"])
        for k, v in self.workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(self.crypto_helper, v["private_key"])
        tx_hash = self.crypto_helper.hash(transaction.get_json())
        self.network_interface.sendTransaction(transaction)
        return tx_hash

    def send_task_transaction(self, task_def):
        transaction = TransactionFactory.create_transcation(task_def)
        for k, v in self.workflow_json["wallet"].items():
            if v["public_key"] == transaction.sender:
                transaction.sign_transaction(self.crypto_helper, v["private_key"])
        tx_hash = self.crypto_helper.hash(transaction.get_json())
        self.network_interface.sendTransaction(transaction)
        return tx_hash

    def read_workflow_json(self):
        with open(self.demo_workflow_file_path, 'r') as file:
            self.workflow_json = json.load(file)[0]

    # def get_transaction_hash(self, task_name):
    #     transaction = TransactionFactory.create_transcation(self.workflow_json[transaction])
    #     print(self.crypto_helper.hash(transaction.get_json()))

    def run_workflow(self, workflow_id):
        self.workflow_json["workflow"]["workflow_id"] = workflow_id
        wf_tx_hash = self.send_workflow_transaction()
        print("WFTX hash for workflow id {}:{}".format(workflow_id, wf_tx_hash))
        public_key = self.workflow_json["workflow"]["sender"]
        received_wf_tx = [tx for tx in self.network_interface.search_transaction_from_receiver(public_key)
                          if tx.payload['workflow_id'] == workflow_id]
        previous_len = 0
        prev_tx_hash = wf_tx_hash

        num_processes = len([key for key in self.workflow_json.keys() if "step" in key])

        # Check if the previous transaction is mined, if yes send the next one in line
        while len(received_wf_tx) <= num_processes:
            if previous_len == len(received_wf_tx):
                sleep(0.1)  # TODO might be smaller?
                received_wf_tx = [tx for tx in self.network_interface.search_transaction_from_receiver(public_key)
                                  if tx.payload['workflow_id'] == workflow_id]
            else:
                print("Process {}:previous mined!".format(workflow_id))
                prev_transaction = self.network_interface.requestTransaction(prev_tx_hash)[0]
                if len(received_wf_tx) == 1:
                    workflow_transaction_hash = wf_tx_hash
                else:
                    workflow_transaction_hash = prev_transaction.payload["workflow_transaction"]
                task_name = "step_{}".format(len(received_wf_tx)-1)
                task_def = self.workflow_json[task_name]
                task_def["workflow_id"] = workflow_id
                task_def["workflow_transaction"] = workflow_transaction_hash
                task_def["previous_transaction"] = prev_tx_hash
                tx_hash = self.send_task_transaction(task_def)
                prev_tx_hash = tx_hash
                previous_len += 1
                print("TX hash for process {}:{}".format(workflow_id, tx_hash))
        print("Full wf completed for process: {}.".format(workflow_id))

    def run_benchmarking(self, num_workflows):
        proc = []
        for i in range(num_workflows):
            p = Process(target=self.run_workflow, args=(i + 1,))
            proc.append(p)

        for p in proc:
            p.start()

        for p in proc:
            p.join()

