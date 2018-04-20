
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
