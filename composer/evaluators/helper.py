import json
import time
import re
import sys


def importNodeLog(path):
    _data = []

    with open(path, "r") as f:
        _data = json.loads(f.read())

    print("Loaded {} elements".format(len(_data)))

    data = []

    for d in _data:
        ds = d.split(":")
        _type = "UNKNOWN"

        output_message = ":".join(ds[1:])

        me = re.search('\{(.*)\}', output_message, re.DOTALL)

        if ds[1].startswith("Peers"):
            _type = "PEERS"
        elif ds[1].startswith("Added new block ---"):
            _type = "ADD_BLOCK"
            re_block_hash = re.search("Added new block ---\s*([a-zA-Z0-9]*)\s*\{.*", output_message, re.DOTALL)
            data.append({"time": time.localtime(float(ds[0])), "type": _type, "hash": re_block_hash.group(1), "data": json.loads(me.group(0).replace("'", '"').replace("None", '"None"'))})
            continue
        elif ds[1].startswith("Added transaction to pool"):
            _type = "ADD_TRANSACTION"

        assert _type != "UNKNOWN"

        data.append({"time": time.localtime(float(ds[0])), "type": _type, "data": me.group(0)})

    return data


def getCleanedBlockLog(nodelog):
    """ Returns the chain of blocks without orphaned branches
    """
    data = list(filter(lambda x: x["type"] == "ADD_BLOCK", nodelog))

    data = list(sorted(data, key=lambda x: x["data"]["nr"]))

    if len(data) == 0:
        return []

    _data = []

    index = len(data) - 1
    # take the last block as a start
    _data.append(data[index])

    while index > 0:
        index -= 1
        while data[index]["hash"] != _data[-1]["data"]["predecessorBlock"] and index > 0:
            index -= 1

        _data.append(data[index])

    return _data
