import json

class Block:
    def __init__(self):
        self.__block_number = None
        self.__timestamp = None
        self.__merkle_tree_root = None
        self.__predecessor_hash = None
        self.__nonce = None
        self.__block_creator_id = None
        self.__transactions = []

    def getJson(self):
        pass

    def getPredecessorHash(self):
        return self.__predecessor_hash

    def returnTransactions(self):
        # return all transactions in the block to the transaction pool
        pass
