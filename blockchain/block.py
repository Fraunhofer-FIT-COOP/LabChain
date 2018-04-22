import hashlib, json, sys

state = {u'X':50, u'Y':50}  # the initial state

def __init__(self):
        self.__block_number = None
        self.__timestamp = None
        self.__merkle_tree_root = None
        self.__predecessor_hash = None
        self.__nonce = None
        self.__block_creator_id = None
        self.__transactions = []

def add_block(txns, chain):
        parent_block = chain[-1]
        parent_hash = parentBlock[u'hash']

        block = {'block_number': len(self.chain) + 1,
                 'timestamp': time(),
                 'transactions': self.transactions,
                 'nonce': nonce,
                 'previous_hash': previous_hash,
                 'parentBlock':parent_block,
                 'parent_hash':parent_hash
                 }
        return block

    blockSizeLimit = 100  ##some random number

while len(txnbuffer) > 0:
        bufferBeginSize = len(txnBuffer)

        txnList = []
        while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
            newTxn = txnBuffer.pop()
            validTxn = isValidTxn(newTxn, state)  # This should return False if the txn is invalid

            if validTxn:
                txnList.append(newTxn)  ## if valid append to the list and update it
                state = updateState(newTxn, state)
            else:
                print("Transaction Flushed")
                sys.stdout.flush()  ## check this command, I took this from some code on google
                continue  # Ignoring invalid transaction and continue

        ## Make a block
        myBlock = add_block(txnList, chain)
        chain.append(myBlock)

 ##   def getJson(self):
 ##       pass

 #  def getPredecessorHash(self):
 #       return self.__predecessor_hash

 #   def returnTransactions(self):
        # return all transactions in the block to the transaction pool
#        pass
