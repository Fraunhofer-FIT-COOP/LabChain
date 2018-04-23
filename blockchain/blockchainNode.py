import datetime
import threading
import time

from blockchain.block import Block
from blockchain.blockchain import BlockChain

#should be fetched from config file


mine_scheduling_frequency_sec = 600
block_transaction_size = 10

#this method just handles the periodic checking to mine incase the mining has't begun because of less transactions
#to start mining based on number of transactions, there needs to be either a discussion on few approaches
def block_mine_timer():
    next_call = time.time()
    while True:
        #check the last call of mine from consensus component
        if consensus.last_mine_time_sec >= mine_scheduling_frequency_sec:
            transactions = txpool.get_transcations(block_transaction_size)
            block = Block(transactions)
            consensus.mine(block)
            blockchain.addBlockCreated(block)
        next_call = next_call + (mine_scheduling_frequency_sec - consensus.last_mine_time_sec)
        time.sleep(next_call - time.time())

if __name__ == '__main__':
    #initialie every other component
    print("\nInitializing BlockChain Node\n")
    consensus = None
    txpool = None
    blockchain = BlockChain()

    #start the scheduler for mining
    mineThread = threading.Thread(target=block_mine_timer)
    mineThread.start()
