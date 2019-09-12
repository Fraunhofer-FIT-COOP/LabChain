""" Evaluates the transactions per block
"""
import sys
import time
import matplotlib.pyplot as plt

from helper import importNodeLog, getCleanedBlockLog


data = getCleanedBlockLog(importNodeLog(sys.argv[1]))

data = list(filter(lambda x: x["type"] == "ADD_BLOCK", data))

x = []
y = []
y_2 = []
y_3 = []

data = list(sorted(data, key=lambda x: x["data"]["nr"]))

for i in range(len(data) - 1):
    x.append(data[i]["data"]["nr"])

    # check for branching ; should be cleaned up
    assert data[i + 1]["data"]["nr"] != data[i]["data"]["nr"]

    y.append(data[i + 1]["data"]["timestamp"] - data[i]["data"]["timestamp"])
    y_3.append(time.mktime(data[i + 1]["time"]) - time.mktime(data[i]["time"]))
    y_2.append(data[i]["data"]["difficulty"])

plt.plot(x, y, label="Mining time for block")
plt.plot(x, y_2, label="Difficulty")
plt.plot(x, y_3, label="Mining time of logs")
plt.xlabel("Block number")
plt.grid(True)

plt.legend()
plt.show()
