from typing import Dict
from ast import literal_eval

from labchain.util.TransactionFactory import TransactionFactory
from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.datastructure.taskTransaction import WorkflowTransaction
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper

class Task:
    def __init__(self, workflow_id, workflow_transaction_hash,previous_transaction_hash):
        self.workflow_id = workflow_id
        self.workflow_transaction_hash = workflow_transaction_hash
        self.previous_transaction_hash = previous_transaction_hash


class TasksManeger:

    @staticmethod
    def check_tasks(network_interface,public_key) -> [TaskTransaction]:
        crypto_helper = CryptoHelper.instance()
        received = network_interface.search_transaction_from_receiver(public_key)
        send = network_interface.search_transaction_from_sender(public_key)
        received_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in received if 'workflow_id' in t.payload]
        send_task_transaction = [TaskTransaction.from_json(t.get_json_with_signature()) for t in send if 'workflow_id' in t.payload]
        send_task_transaction = [t for t in send_task_transaction if t.type == '2']
        received_task_transaction_dict = {crypto_helper.hash(t.get_json()): t for t in received_task_transaction}
        send_task_transaction_dict = {t.previous_transaction: t for t in send_task_transaction}
        diff = {k: received_task_transaction_dict[k] for k in set(received_task_transaction_dict)- set(send_task_transaction_dict)}
        return [diff[k] for k in diff]

    @staticmethod
    def get_tasks_objects_from_task_transactions(transactions):
        crypto_helper = CryptoHelper.instance()
        tasks = []
        for t in transactions:
            if isinstance(t.payload, Dict):
                if t.payload['transaction_type'] == '1':
                    workflow_id = t.payload['workflow_id']
                    workflow_transaction_hash = crypto_helper.hash(t.get_json())
                    task = Task(workflow_id,workflow_transaction_hash,workflow_transaction_hash)
                    tasks.append(task)
                if t.payload['transaction_type'] == '2':
                    workflow_id = t.payload['workflow_id']
                    workflow_transaction_hash = t.payload['workflow_transaction']
                    previous_transaction_hash = crypto_helper.hash(t.get_json())
                    task = Task(workflow_id,workflow_transaction_hash,previous_transaction_hash)
                    tasks.append(task)
        return tasks


    

