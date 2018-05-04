from mock.transaction import Transaction


class TransactionFactory:

    def __init__(self):
        pass

    def create_transaction(self, sender, receiver, payload, signature):
        return Transaction(sender, receiver, payload, signature)
