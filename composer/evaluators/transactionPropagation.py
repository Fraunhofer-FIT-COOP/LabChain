""" Computes the necessary times for propagating a transaction throughout the network
"""
import pprint
import time
import re
import os
import sys
import matplotlib.pyplot as plt

from helper import importNodeLog

regex = sys.argv[1].split("/")[-1].replace('*', "[0-9]*")

benchmark_dir = os.path.dirname(sys.argv[1])
_files = [f for f in os.listdir(benchmark_dir) if re.match(regex, f)]

files = []

node_name_regex = r".*(labchain_[0-9]*)\.json"

for _file in _files:
    me = re.match(node_name_regex, _file)
    files.append([me.group(1), _file])

print(files)

add_transactions_to_pool_events = {}

for _file in files:
    data = importNodeLog(os.path.join(benchmark_dir, _file[1]))
    data = list(filter(lambda x: x["type"] == "ADD_TRANSACTION", data))

    for d in data:
        payload = d["data"]["payload"]
        evts = add_transactions_to_pool_events.get(payload, [])
        evts.append({"node": _file[0], "time": time.mktime(d["time"])})
        add_transactions_to_pool_events[payload] = evts

for evt in add_transactions_to_pool_events:
    print(evt)
    print(add_transactions_to_pool_events[evt])

# fig = plt.figure()
#
# ax = fig.add_subplot(111)
#
# ax.plot(["sample1", "sample2"], [1, 2])
# ax.set_xticklabels(["sample1", "sample2"])
#
# plt.show()
