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

fig = plt.figure()
host = fig.add_subplot(111)

par1 = host.twinx()

color1 = plt.cm.viridis(0)
color2 = plt.cm.viridis(0.5)

host.plot(x, y, color=color1, label="Mining time for block")
par1.plot(x, y_2, color=color2, label="Difficulty")
par1.set_ylabel("Difficulty")
par1.yaxis.label.set_color(color2)
#plt.plot(x, y_3, label="Mining time of logs")
host.set_xlabel("Block number")
host.set_ylabel("Mining time for block [s]")
host.yaxis.label.set_color(color1)
# plt.grid(True)
plt.title("{} - Avg mining time: {}, Avg difficulty: {}".format(sys.argv[1], sum(y) / len(y), sum(y_2) / len(y_2)))

# plt.legend()
plt.show()
