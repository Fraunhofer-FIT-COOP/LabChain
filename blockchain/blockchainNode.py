import configparser
import sys
import threading
import time

from Mock.consensus import Consensus
from Mock.networkInterface import NetworkInterface
from Mock.txPool import TxPool
from blockchain.blockchain import BlockChain


# this method just handles the periodic checking to mine incase the
# mining has't begun because of less transactions to start mining based
# on number of transactions, there needs to be either a discussion on
# few approaches
def block_mine_timer(mine_freq, num_of_transactions, blockchain_obj,
                     txn_pool_obj, consensus_obj):
    next_call = time.time()
    while True:
        # check the last call of mine from consensus component
        if consensus.last_mine_time_sec >= mine_freq:
            transactions = txn_pool_obj.get_transcations(num_of_transactions)
            # should the blockchain,py create block or Block,py create block
            block = blockchain_obj.create_block(transactions)
            consensus_obj.mine(block)
            # instead of returning nonce,
            # nonce should be added in the block object
            # have to check if other node already created a block
            blockchain_obj.add_block(True, block)

        next_call += (mine_freq - consensus_obj.last_mine_time_sec)
        time.sleep(next_call - time.time())


if __name__ == '__main__':
    # initialize every other component
    print("\nInitializing BlockChain Node\n")

    config = configparser.ConfigParser()

    try:
        config.read('resources/node_configuration.ini')
    except:
        # Need to do proper handling of exceptions
        pass

    try:
        mine_freq = config.getint(section='MINING',
                                  option='MINE_SCHEDULING_FREQUENCY_SEC')
        num_of_transactions = config.getint(section='MINING',
                                            option='BLOCK_TRANSACTION_SIZE')
    except:
        print("Configuration options missing, can't start module")
        # maybe could start with the default values, unless file locations are missing
        sys.exit(0)

    # singleton of these classes should be better
    consensus = Consensus()
    txpool = TxPool()
    networkInterface = NetworkInterface()
    blockchain = BlockChain(consensus)

    # start the scheduler for mining
    mine_thread = threading.Thread(target=block_mine_timer,
                                   kwargs=dict(mine_freq=mine_freq,
                                               num_of_transactions=num_of_transactions,
                                               blockchain_obj=blockchain,
                                               txn_pool_obj=txpool,
                                               consensus_obj=consensus))
    mine_thread.start()
