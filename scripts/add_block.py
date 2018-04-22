import hashlib, json, sys


def addBlock(txns, chain):
    parentBlock = chain[-1]
    parentHash = parentBlock['hash']
    blockNumber = parentBlock['contents']['blockNumber'] + 1
    txnCount = len(txns)
    blockContents = {'blockNumber': blockNumber, 'parentHash': parentHash,
                     'txnCount': len(txns), 'txns': txns}
    blockHash = hashMe(blockContents)
    block = {'hash': blockHash, 'contents': blockContents}

    return block

blockSizeLimit = 100 ##some random number

while len(txnbuffer)>0:
    bufferBeginSize = len(txnBuffer)

    txnList = []
    while (len(txnBuffer) > 0) & (len(txnList) < blockSizeLimit):
        newTxn = txnBuffer.pop()
        validTxn = isValidTxn(newTxn, state)  # This should return False if the txn is invalid

        if validTxn:
            txnList.append(newTxn) ## if valid append to the list and update it
            state = updateState(newTxn, state)
        else:
            print("Transaction Flushed")
            sys.stdout.flush() ## check this command, I took this from some code on google
            continue  # Ignoring invalid transaction and continue

    ## Make a block
    myBlock = addBlock(txnList, chain)
    chain.append(myBlock)