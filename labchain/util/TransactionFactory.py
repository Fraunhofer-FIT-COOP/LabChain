from labchain.workflow.taskTransaction import TaskTransaction
from labchain.workflow.taskTransaction import WorkflowTransaction
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import TYPE_SIMPLE_TRANSACTION, TYPE_WORKFLOW_TRANSACTION, TYPE_TASK_TRANSACTION


class TransactionFactory:

    @staticmethod
    def create_transaction(transaction_data):
        transaction_type = TYPE_SIMPLE_TRANSACTION
        try:
            transaction_type = int(transaction_data["transaction_type"])
        except ValueError as e:
            raise Exception("Invalid transaction type: {}".format(transaction_type))
        except Exception as e:
            raise e

        if transaction_type == TYPE_SIMPLE_TRANSACTION:
            t = Transaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                            transaction_data['payload'], transaction_data['signature'])
        elif transaction_type == TYPE_WORKFLOW_TRANSACTION:
            t = WorkflowTransaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                                    transaction_data['payload'], transaction_data['signature'])
        elif transaction_type == TYPE_TASK_TRANSACTION:
            t = TaskTransaction(transaction_data['sender'], transaction_data['receiver'], transaction_type,
                                transaction_data['payload'], transaction_data['signature'])
        else:
            raise Exception("Invalid transaction type: {}".format(transaction_type))
        t.transaction_hash = CryptoHelper.instance().hash(t.get_json())
        return t
