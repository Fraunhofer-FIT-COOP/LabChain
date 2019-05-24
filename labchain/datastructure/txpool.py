import logging

from labchain.datastructure.transaction import Transaction
from labchain.datastructure.taskTransaction import TaskTransaction


class TxPool:
    _singleton = None
    _first_time = True

    def __init__(self, crypto_helper_obj):
        #  Note: Re-look this logic again later
        if self._first_time:
            self._transactions = []
            self._crypto_helper = crypto_helper_obj
            self._first_time = False

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = object.__new__(TxPool)
        return cls._singleton

    def get_transaction(self):
        return self._transactions.pop()

    def get_transaction_by_hash(self, transaction_hash):
        """tuple with 1st element as transaction and 2nd element as block_hash"""
        for transaction in self._transactions:
            if transaction.transaction_hash == transaction_hash:
                return (transaction, None)
        return None, None

    def get_transactions(self, count, remove_result=True):
        transactions = self._transactions[:count]
        if remove_result:
            self._transactions = self._transactions[count:]
        return transactions

    def get_task_transactions(self):
        task_transactions = []
        for transaction in self._transactions:
            if isinstance(transaction, TaskTransaction):
                task_transactions.append(transaction)
        return task_transactions

    def remove_transaction(self, transaction):
        if transaction in self._transactions:
            self._transactions.remove(transaction)
            return True
        return False

    def add_transaction_if_not_exist(self, transaction):
        if isinstance(transaction, Transaction):
            if transaction not in self._transactions and \
                    transaction.validate_transaction(self._crypto_helper):
                if not transaction.transaction_hash:
                    hash_val = self._crypto_helper.hash(transaction.get_json())
                    transaction.transaction_hash = hash_val
                self._transactions.append(transaction)
                logging.info('Added transaction to pool: {}'.format(transaction))
                return True
            else:
                return False
        return False

    def get_transaction_count(self):
        return len(self._transactions)

    def return_transactions_to_pool(self, transactions):
        status = True
        for transaction in transactions:
            status = status and self.add_transaction_if_not_exist(transaction)
        return status
