import configparser
import sys
import threading
import time

from labchain.txpool import TxPool
from mock.consensus import Consensus
from mock.networkInterface import NetworkInterface
from labchain.blockchain import BlockChain


def block_mine_timer(mine_freq, block_transactions_size, blockchain_obj,
                     txpool_obj, consensus_obj):
    """ Thread which periodically checks to mine
    Note: to start mining based on number of transactions,
    there needs to be either a discussion on few approaches

        Args:
            mine_freq (integer): periodicity of mining in seconds
            block_transactions_size (integer): max transactions in a block
            blockchain_obj:
            txpool_obj:
            consensus_obj:

    """
    next_call = time.time()
    while True:
        # check the last call of mine from consensus component
        if consensus.last_mine_time_sec >= mine_freq:
            transactions = txpool_obj.get_transcations(block_transactions_size)
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
    """ initialize every other component
    main method to initialize the block chain node
    and all its components"""

    print("\nInitializing BlockChain Node\n")

    config = configparser.ConfigParser()

    try:
        config.read('resources/node_configuration.ini')
    except RuntimeError:
        #  need to use the correct type of error
        # Need to do proper handling of exceptions
        pass

    try:
        mine_freq = config.getint(section='MINING',
                                  option='MINE_SCHEDULING_FREQUENCY_SEC')
        num_of_transactions = config.getint(section='MINING',
                                            option='BLOCK_TRANSACTION_SIZE')
        block_creator_id = config.get(section='BLOCK',
                                      option='BLOCK_CREATOR_ID')
    except RuntimeError:
        #  need to use the correct type of error
        print("Configuration options missing, can't start module")
        # maybe could start with the default values, unless file locations are missing
        sys.exit(0)

    # singleton of these classes should be better
    consensus = Consensus()
    txpool = TxPool()
    networkInterface = NetworkInterface()
    blockchain = BlockChain(consensus, txpool, block_creator_id)

    # start the scheduler for mining
    mine_thread = threading.Thread(target=block_mine_timer,
                                   kwargs=dict(mine_freq=mine_freq,
                                               num_of_transactions=num_of_transactions,
                                               blockchain_obj=blockchain,
                                               txn_pool_obj=txpool,
                                               consensus_obj=consensus))
    mine_thread.start()
