
class Block:

    def __init__(self, index, timestamp, data):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.pre_hash = None
        self.tree_hash = None
        self.nonce = 0
        self.creator = None

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass


class CryptoHelper:
    def __init__(self, data):
        self.data = data

    def hash(self, data):
        self.data = data
        # TO Be Implemented to return Hash
        return data


class MockCryptoHelper:

    def hash(data):
        # TO Be Implemented to return Hash
        return "000000000000" + data
    hash = staticmethod(hash)
