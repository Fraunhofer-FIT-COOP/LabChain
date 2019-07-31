#!/bin/sh

cd /app/LabChain

if [ "${PEER}" == "NONE" ] ; then
        python3 ./node.py --port ${PORT} --very-verbose --peer-discovery
else
        python3 ./node.py --port ${PORT} --very-verbose --peers ${PEER}
fi
