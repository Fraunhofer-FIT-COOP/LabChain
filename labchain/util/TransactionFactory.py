from labchain.datastructure.transaction import Transaction
from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.datastructure.taskTransaction import WorkflowTransaction

class TransactionFactory:

    @staticmethod
    def create_transcation(transaction_data):
        if "transaction_type" in transaction_data['payload']:
            transaction_type = transaction_data['payload']['transaction_type']
            if (transaction_type == '0'):
                return Transaction(transaction_data['sender'], transaction_data['receiver'],transaction_data['payload'], transaction_data['signature'])
            if (transaction_type == '1'):
                return WorkflowTransaction(transaction_data['sender'], transaction_data['receiver'],transaction_data['payload'],transaction_data['signature'])
            if (transaction_type == '2'):
                return TaskTransaction(transaction_data['sender'], transaction_data['receiver'],transaction_data['payload'], transaction_data['signature'])
        else:
            return Transaction(transaction_data['sender'], transaction_data['receiver'],transaction_data['payload'], transaction_data['signature'])

