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

if [ "${BENCHMARK}" != "NONE" ] ; then
        CONFIG="${CONFIG} --benchmark ${BENCHMARK}"
fi

exec python3 ${CONFIG}
