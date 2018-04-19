class Consensus:

    def __init__(self, configuration):
        self.configuration = configuration

    def validate(self, block, nonce):
        zeros_array = "0" * (self.configuration + 1)
        counter = 0
        while block.hash[:self.configuration] != zeros_array:
            counter += 1
            block.hash = block.generate_hash()
        if nonce == block.nonce:
            return True
        else:
            return False

    def mine(block, difficulty):
        zeros_array = "0" * (difficulty + 1)
        while block.hash[:difficulty] != zeros_array:
            block.nonce = block.nonce + 1
            block.hash = block.generate_hash()
        return block.nonce
    mine = staticmethod(mine)


class Block:

    def __init__(self, index, timestamp, data):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.pre_hash = None
        self.hash = self.generate_hash()
        self.nonce = 0

    def generate_hash(self):
        return self.data  # TO Be Implemented to return Hash

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass
