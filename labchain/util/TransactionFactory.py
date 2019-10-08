from labchain.workflow.taskTransaction import TaskTransaction
from labchain.workflow.taskTransaction import WorkflowTransaction
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper

#   Transaction types:
#   0: Normal transaction
#   1: Workflow transaction (includes workflow definition)
#   2: Task transaction (includes changes on the document inside the workflow)


class TransactionFactory:

    @staticmethod
    def create_transaction(transaction_data):
        transaction_type = 0
        try:
            transaction_type = transaction_data["transaction_type"]
        except:
            pass

        if transaction_type is '0':
            t = Transaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                            transaction_data['payload'], transaction_data['signature'])
        elif transaction_type is '1':
            t = WorkflowTransaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                                    transaction_data['payload'], transaction_data['signature'])
        else:   #elif 'document' in transaction_data['payload']:
            t = TaskTransaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                                transaction_data['payload'], transaction_data['signature'])
        t.transaction_hash = CryptoHelper.instance().hash(t.get_json())
        return t
