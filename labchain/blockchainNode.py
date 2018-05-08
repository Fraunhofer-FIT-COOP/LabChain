import configparser
import sys
import threading
import time
import uuid

from labchain.txpool import TxPool
from mock.cryptoHelper import CryptoHelper
from mock.consensus import Consensus
from mock.networkInterface import NetworkInterface
from labchain.blockchain import BlockChain


NODE_CONFIG_FILE = 'resources/node_configuration.ini'


def block_mine_timer(mine_freq, block_transactions_size, blockchain,
                     txpool, consensus):
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
            transactions = txpool.get_transcations(block_transactions_size)
            # should the blockchain,py create block or Block,py create block
            block = blockchain.create_block(transactions)
            consensus.mine(block)
            # instead of returning nonce,
            # nonce should be added in the block object
            # have to check if other node already created a block
            blockchain.add_block(True, block)

        next_call += (mine_freq - consensus.last_mine_time_sec)
        time.sleep(next_call - time.time())

def on_new_transaction_received():
    # This method wakes up the txpool thread
    pass

def initializeNode():
    """ Initialize every componenent of the node"""

    try:
        config = configparser.ConfigParser()
        config.read(NODE_CONFIG_FILE)
    except:
        print('Node Configuration file is corrupt or non-existent, \
              exiting node startup.... \n')
        sys.exit(0)

    try:
        mine_freq = config.getint(section='MINING',
                                  option='MINE_SCHEDULING_FREQUENCY_SEC')
        num_of_transactions = config.getint(section='MINING',
                                            option='BLOCK_TRANSACTION_SIZE')
    except:
        print("Node configuration file is corrupt, exiting node startup" \
              ".... \n")
        sys.exit(0)

    consensus = Consensus()
    txpool = TxPool()
    networkInterface = NetworkInterface()
    crypto_helper = CryptoHelper()

    # Generate the node ID using host ID
    node_uuid = str(uuid.uuid1())
    node_id = node_uuid[:node_uuid.find('-')]

    blockchain = BlockChain(consensus, txpool, node_id, crypto_helper)

    # start the scheduler for mining
    mine_thread = threading.Thread(target=block_mine_timer,
                                   kwargs=dict(mine_freq=mine_freq,
                                               num_of_transactions=num_of_transactions,
                                               blockchain_obj=blockchain,
                                               txn_pool_obj=txpool,
                                               consensus_obj=consensus))
    mine_thread.start()

if __name__ == '__main__':
    initializeNode()
