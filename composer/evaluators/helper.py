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

        me = re.search(r'\{(.*)\}', output_message, re.DOTALL)

        if ds[1].startswith("Peers"):
            _type = "PEERS"
        elif ds[1].startswith("Added new block ---"):
            _type = "ADD_BLOCK"
            try:
                re_block_hash = re.search(r"Added new block ---\s*([a-zA-Z0-9]*)\s*\{.*",
                                          output_message, re.DOTALL)
                data.append({"time": time.localtime(float(ds[0])), "type": _type,
                             "hash": re_block_hash.group(1),
                             "data": json.loads(me.group(0)
                                                .replace("'", '"').replace("None", '"None"'))})
            except Exception as regex_error:
                print(regex_error)
                print(me.group(0))
                raise regex_error
            continue
        elif ds[1].startswith("Added transaction to pool"):
            _type = "ADD_TRANSACTION"
            try:
                data.append({"time": time.localtime(float(ds[0])),
                             "type": _type,
                             "data": json.loads(me.group(0)
                                                .replace("'", '"').replace("None", '"None"'))})
            except Exception as e:
                print(e)
                print(me.group(0))
                raise e
            continue

        assert _type != "UNKNOWN"

        data.append({"time": time.localtime(float(ds[0])), "type": _type, "data": me.group(0)})

    return data


def get_events_before_time(nodelog, _time):
    """ Returns the events before and at the given time
    """

    cleaned_log = []

    for log in nodelog:
        if log["time"] <= _time:
            cleaned_log.append(log)

    return cleaned_log


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
