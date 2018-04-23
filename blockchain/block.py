class Block:
    def __init__(self, transactions):
        self.__block_number = None
        self.__timestamp = None
        self.__merkle_tree_root = None
        self.__predecessor_hash = None
        self.__nonce = None
        self.__block_creator_id = None
        self.__transactions = transactions

    def get_json(self):
       pass

    def get_predecessor_hash(self):
       return self.__predecessor_hash

    def return_transactions(self):
        # Return all transactions in the block to the transaction pool
        # called if the block created is abut to be deleted
        pass
