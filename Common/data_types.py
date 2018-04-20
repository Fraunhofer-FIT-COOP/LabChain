
class Block:

    def __init__(self, index, timestamp, data):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.pre_hash = None
        self.nonce = 0


    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

class CryptoHelper:

    def __init__(self):
        pass

    def hash(self, data):
        # TO Be Implemented to return Hash
        return data