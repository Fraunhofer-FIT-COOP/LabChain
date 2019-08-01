#!/bin/sh

cd /app/LabChain

CONFIG="./node.py --port ${PORT} --very-verbose"

if [ "${CORS}" != "NONE" ] ; then
        CONFIG="${CONFIG} --cors ${CORS}"
fi

if [ "${PEER}" = "NONE" ] ; then
        CONFIG="${CONFIG} --peer-discovery"
else
        CONFIG="${CONFIG} --peers ${PEER}"
fi

python3 ${CONFIG}
