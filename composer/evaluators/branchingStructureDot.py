""" Provides a DOT file containing the branching structure of the considered node log
"""
import sys

from helper import importNodeLog

data = importNodeLog(sys.argv[1])

data = list(filter(lambda x: x["type"] == "ADD_BLOCK", data))

dot_content = "digraph blockchain {\n"

for d in data:
    block_data = d["data"]
    block_hash = d["hash"]

    predecessor_block = [x for x in data if x["hash"] == block_data["predecessorBlock"]]

    if len(predecessor_block) > 0:
        predecessor_block = predecessor_block[0]
    else:
        continue

    dot_content += "\t \"{}:{}\" -> \"{}:{}\";\n".format(predecessor_block["data"]["nr"], predecessor_block["hash"], d["data"]["nr"], block_hash)

dot_content += "}"

if len(sys.argv) == 2:
    print(dot_content)
    sys.exit()

with open(sys.argv[2], "w") as f:
    f.write(dot_content)
