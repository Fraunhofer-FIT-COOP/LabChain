#!/usr/bin/python3

import sys
import json
from datetime import datetime

data = []

with open(sys.argv[1], "r") as f:
    data = json.loads(f.read())

durations = []

for d in data:
    d["start_time"] = datetime.strptime(d["start_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
    d["end_time"] = datetime.strptime(d["end_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
    durations.append(abs((d["end_time"] - d["start_time"]).total_seconds()))


print(data)
print(durations)
print("Average duration in seconds: {}s".format(float(sum(durations)) / len(durations)))
