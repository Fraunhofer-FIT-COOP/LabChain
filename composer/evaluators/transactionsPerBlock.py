""" Evaluates the transactions per block
"""
import sys
import matplotlib.pyplot as plt

from helper import importNodeLog, getCleanedBlockLog


data = getCleanedBlockLog(importNodeLog(sys.argv[1]))

data = list(filter(lambda x: x["type"] == "ADD_BLOCK", data))

x = []
y = []

for d in data:
    x.append(d["data"]["nr"])
    y.append(len(d["data"]["transactions"]))

plt.plot(x, y)
plt.xlabel("Block number")
plt.ylabel("Transactions per block")
plt.title(sys.argv[1])

plt.show()
