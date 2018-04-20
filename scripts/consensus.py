
class Consensus:

    def __init__(self, configuration):
        self.configuration = configuration

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    def calculate_difficulty(self):
        #   TO-DO:  must be configured somehow
        difficulty = 4
        return difficulty

    def validate(self, block):

        given_nonce = block.nonce
        difficulty = calculate_difficulty()
        zeros_array = "0" * ()

        helper = new CryptoHelper()
        block_hash = helper.hash()#What to take as input?

        return block_hash[0:difficulty] == zeros_array


    def mine(block, difficulty):
        zeros_array = "0" * (difficulty + 1)
        while block.hash[:difficulty] != zeros_array:
            block.nonce = block.nonce + 1
            block.hash = block.generate_hash()
        return block.nonce
    mine = staticmethod(mine)