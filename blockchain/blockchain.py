from block import Block

class BlockChain:
    def __init__(self):
        # will contain key = __block_number, value = Block obj instance
        self.__blockchain = {}
        self.__current_branch_heads = [] # Block object instances

    def addBlockReceived(self):
        pass

    def addBlockCreated(self):
        pass

    def validateBlock(self):
        pass

    def switchToBranch(self):
        pass

    def computeMerkleRoot(self):
        pass
