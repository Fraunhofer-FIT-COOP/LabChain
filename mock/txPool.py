class TxPool:

    def __init__(self):
        self.__transactions_count = 0
        pass

    def get_transaction(self):
        pass

    def get_transactions(self, count):
        pass

    def remove_transaction(self, transaction):
        pass

    def add_transaction_if_not_exist(self, transaction):
        pass

    def get_transaction_count(self):
        return self.__transactions_count

    def return_transactions_to_pool(self, transactions):
        #  check_transaction_signature
        pass