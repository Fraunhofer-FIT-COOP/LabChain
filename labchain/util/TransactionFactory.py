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
    def create_case_transaction(case_ID,controller_public_key,physician_public_key,doctor_public_key,chef_public_key):
        workflow_transaction = {}
        workflow_transaction['sender'] = controller_public_key
        workflow_transaction['receiver'] = physician_public_key
        workflow_transaction['signature'] = None
        workflow_transaction['payload'] = {}
        workflow_transaction['payload']['transaction_type'] = '1'
        workflow_transaction['payload']['workflow_id'] = case_ID
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
    def create_assumed_diagnosis_transaction(case_ID,sender_public_key,receiver_public_key,assumed_diagnosis,workflow_transaction,previous_transaction):
        return TransactionFactory.create_diagnosis_transaction(case_ID,sender_public_key,receiver_public_key,assumed_diagnosis,True,workflow_transaction,previous_transaction)

    @staticmethod
    def create_real_diagnosis_transaction(case_ID,sender_public_key,receiver_public_key,real_diagnosis,workflow_transaction,previous_transaction):
        return TransactionFactory.create_diagnosis_transaction(case_ID,sender_public_key,receiver_public_key,real_diagnosis,False,workflow_transaction,previous_transaction)


    @staticmethod
    def create_diagnosis_transaction(case_ID,sender_public_key,receiver_public_key,diagnosis,is_assumed,workflow_transaction,previous_transaction):
        task_transaction = {}
        task_transaction['sender'] = sender_public_key
        task_transaction['receiver'] = receiver_public_key
        task_transaction['signature'] = None
        task_transaction['payload'] = {}
        task_transaction['payload']['transaction_type'] = '2'
        task_transaction['payload']['workflow_id'] = case_ID
        task_transaction['payload']['document'] = {}
        if is_assumed:
            task_transaction['payload']['document']['assumed_diagnosis'] = diagnosis
        else:
            task_transaction['payload']['document']['real_diagnosis'] = diagnosis
        task_transaction['payload']['in_charge'] = receiver_public_key+ '_1'
        task_transaction['payload']['workflow_transaction'] = workflow_transaction
        task_transaction['payload']['previous_transaction'] = previous_transaction

        return TransactionFactory.create_transcation(task_transaction)
