#!/bin/sh

node-red node-dashboard-app/dash-app.js &
python3 scripts/node_start.py --port 8080 --very-verbose --plot

