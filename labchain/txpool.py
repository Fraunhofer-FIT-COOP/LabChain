from labchain.transaction import Transaction


class TxPool:

    def __init__(self, crypto_helper_obj):
        self._transactions = []
        self._crypto_helper = crypto_helper_obj

    def get_transaction(self):
        return self._transactions.pop()

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
                self._crypto_helper.validate_signature(transaction):
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
