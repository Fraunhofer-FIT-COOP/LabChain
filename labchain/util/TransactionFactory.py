from typing import Dict

from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.datastructure.taskTransaction import WorkflowTransaction
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper


class TransactionFactory:

    @staticmethod
    def create_transcation(transaction_data):
        if isinstance(transaction_data['payload'], Dict):
            transaction_type = transaction_data['payload'].get('transaction_type', '0')
        else:
            transaction_type = '0'
        if transaction_type == '1':
            t = WorkflowTransaction(transaction_data['sender'], transaction_data['receiver'],
                                    transaction_data['payload'], transaction_data['signature'])
        elif transaction_type == '2':
            t = TaskTransaction(transaction_data['sender'], transaction_data['receiver'], transaction_data['payload'],
                                transaction_data['signature'])
        else:
            t = Transaction(transaction_data['sender'], transaction_data['receiver'], transaction_data['payload'],
                            transaction_data['signature'])
        t.transaction_hash = CryptoHelper.instance().hash(t.get_json())
        return t

    @staticmethod
    def create_case_transaction(controller_public_key,physician_public_key,doctor_public_key,chef_public_key):
        workflow_transaction = {}
        workflow_transaction['sender'] = controller_public_key
        workflow_transaction['receiver'] = physician_public_key
        workflow_transaction['signature'] = None
        workflow_transaction['payload'] = {}
        workflow_transaction['payload']['transaction_type'] = '1'
        workflow_transaction['payload']['workflow_id'] = '34'
        workflow_transaction['payload']['document'] = {}
        workflow_transaction['payload']['document']['assumed_diagnosis'] = 'None'
        workflow_transaction['payload']['document']['real_diagnosis'] = 'None'
        workflow_transaction['payload']['in_charge'] = physician_public_key+ '_1'
        workflow_transaction['payload']['processes'] = {}
        workflow_transaction['payload']['processes'][physician_public_key + '_1'] = [doctor_public_key + '_1']
        workflow_transaction['payload']['processes'][doctor_public_key + '_1'] = [chef_public_key + '_1']

        workflow_transaction['payload']['permissions'] = {}
        workflow_transaction['payload']['permissions']['assumed_diagnosis'] = [physician_public_key + '_1']
        workflow_transaction['payload']['permissions']['real_diagnosis'] = [doctor_public_key + '_1']
        return TransactionFactory.create_transcation(workflow_transaction)

    @staticmethod
    def create_assumed_diagnosis_transaction(sender_public_key,receiver_public_key,assumed_diagnosis):
        """method for sending assumed diagnosis or real diagnosis"""
        task_transaction = {}
        task_transaction['sender'] = sender_public_key
        task_transaction['receiver'] = receiver_public_key
        task_transaction['signature'] = None
        task_transaction['payload'] = {}
        task_transaction['payload']['transaction_type'] = '2'
        task_transaction['payload']['workflow_id'] = '34'
        task_transaction['payload']['document'] = {}
        task_transaction['payload']['document']['assumed_diagnosis'] = assumed_diagnosis
        task_transaction['payload']['in_charge'] = receiver_public_key+ '_1'
        task_transaction['payload']['workflow_transaction'] = "TODO: put transaction hash here"
        task_transaction['payload']['previous_transaction'] = "TODO: put transaction hash here"

        return TransactionFactory.create_transcation(task_transaction)
