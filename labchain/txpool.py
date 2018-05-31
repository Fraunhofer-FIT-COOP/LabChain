from labchain.transaction import Transaction


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
        #TODO : search pool for transaction with given hash
        """tuple with 1st element as transaction and 2nd element as block_hash"""
        pass

    def get_transactions(self, count):
        transactions = self._transactions[:count]
        self._transactions = self._transactions[count:]
        return transactions

    def remove_transaction(self, transaction):
        if transaction in self._transactions:
            self._transactions.remove(transaction)
            return True
        return False

    def add_transaction_if_not_exist(self, transaction):
        if isinstance(transaction, Transaction):
            if transaction not in self._transactions and \
                    transaction.validate_transaction(self._crypto_helper):
                self._transactions.append(transaction)
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

