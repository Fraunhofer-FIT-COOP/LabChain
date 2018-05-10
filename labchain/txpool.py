from labchain.transaction import Transaction


class TxPool:

    def __init__(self, crypto_helper_obj):
        self.__transactions = []
        self.__crypto_helper = crypto_helper_obj

    def get_transaction(self):
        return self.__transactions.pop()

    def get_transactions(self, count):
        transactions = self.__transactions[:count]
        self.__transactions = self.__transactions[count:]
        return transactions

    def remove_transaction(self, transaction):
        if transaction in self.__transactions:
            self.__transactions.remove(transaction)
            return True
        return False

    def add_transaction_if_not_exist(self, transaction):
        if isinstance(transaction, Transaction):
            if transaction not in self.__transactions and self.__crypto_helper.validate_signature(transaction):
                self.__transactions.append(transaction)
                return True
            else:
                return False
        return False

    def get_transaction_count(self):
        return len(self.__transactions)

    def return_transactions_to_pool(self, transactions):
        status = True
        for transaction in transactions:
            status = status and self.add_transaction_if_not_exist(transaction)
        return status
