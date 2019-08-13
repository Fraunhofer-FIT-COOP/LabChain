#!/usr/bin/python3

import sys
import json
from datetime import datetime

data = []

with open(sys.argv[1], "r") as f:
    data = json.loads(f.read())

durations = []

for d in data:
    durations.append(abs(int(d["start_time"]) - int(d["end_time"])))


print(data)
print(durations)
print("Average duration in seconds: {}s".format(float(sum(durations)) / len(durations)))
print("Average duration in minutes: {}s".format(float(sum(durations)) / len(durations) / 60))
print("Average duration in hours: {}s".format(float(sum(durations)) / len(durations) / 60 / 60))
