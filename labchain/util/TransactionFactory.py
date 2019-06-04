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
