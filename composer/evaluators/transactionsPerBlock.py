""" Evaluates the transactions per block
"""
import json
import time
import sys
import re
import matplotlib.pyplot as plt


def importNodeLog(path):
    _data = []

    with open(path, "r") as f:
        _data = json.loads(f.read())

    print("Loaded {} elements".format(len(_data)))

    data = []

    for d in _data:
        ds = d.split(":")
        _type = "UNKNOWN"

        me = re.search('\{(.*)\}', ":".join(ds[1:]), re.DOTALL)

        if ds[1].startswith("Peers"):
            _type = "PEERS"
        elif ds[1].startswith("Added new block ---"):
            _type = "ADD_BLOCK"
            data.append({"time": time.localtime(float(ds[0])), "type": _type, "data": json.loads(me.group(0).replace("'", '"').replace("None", '"None"'))})
            continue
        elif ds[1].startswith("Added transaction to pool"):
            _type = "ADD_TRANSACTION"

        assert _type != "UNKNOWN"

        data.append({"time": time.localtime(float(ds[0])), "type": _type, "data": me.group(0)})

    return data


data = importNodeLog(sys.argv[1])

data = list(filter(lambda x: x["type"] == "ADD_BLOCK", data))

x = []
y = []

for d in data:
    x.append(d["data"]["nr"])
    y.append(len(d["data"]["transactions"]))

plt.plot(x, y)
plt.xlabel("Block number")
plt.ylabel("Transactions per block")

plt.show()
