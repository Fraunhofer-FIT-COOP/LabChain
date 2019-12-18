""" Computes the transaction throughput as specified by the
Hyperledger performance metrics

Transaction Throughput = Total committed transactions / total time in seconds

This evaluator will create a graph showing on the x axis the time, which
correlates with the number of already transmitted transactions and the number
of blocks.

On the y axis the transaction throughput is depicted.
"""
import sys
import time
import matplotlib.pyplot as plt

from helper import importNodeLog, getCleanedBlockLog, get_events_before_time, importBenchmarkLog

data = importNodeLog(sys.argv[1])
data_add_block = getCleanedBlockLog(data)

data_add_block = list(filter(lambda x: x["type"] == "ADD_BLOCK", data_add_block))
data_add_block.reverse()
data_add_transaction = list(filter(lambda x: x["type"] == "ADD_TRANSACTION", data))

benchmark_data = importBenchmarkLog(sys.argv[2])

first_transaction_time = sorted(benchmark_data, key=lambda x: x["start_time"])[0]

x = []
y = []


def compute_transaction_throughput(block):
    """ Computes the transactions throughput at the time of the given block
    """
    block_time = block["time"]
    print("{} - {}".format(time.mktime(block_time), first_transaction_time["start_time"]))

    added_transactions_until_block = get_events_before_time(data_add_transaction, block_time)

    blocks_until_block = get_events_before_time(data_add_block, block_time)

    confirmed_transaction_count = sum([len(x["data"]["transactions"]) for x in blocks_until_block])

    time_spend = time.mktime(block_time) - first_transaction_time["start_time"]

    if time_spend <= 0:
        time_spend = 1

    if len(added_transactions_until_block) > 0:
        return confirmed_transaction_count / time_spend
    else:
        return 0


for d in data_add_block:
    x.append(d["data"]["nr"])
    y.append(compute_transaction_throughput(d))

plt.plot(x, y)
plt.xlabel("Block number")
plt.ylabel("Transactions throughput")
plt.title(sys.argv[1])

plt.show()
