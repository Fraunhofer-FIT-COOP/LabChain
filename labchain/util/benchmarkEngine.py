""" The benchmark engine provides functionality to store important
process information. These information can be stored and outputted into
a file.
"""

import logging
import json
import time
from threading import Lock

logger = logging.getLogger(__name__)


class __BenchmarkEngine:
    def __init__(self):
        self._log = []
        self.filename = "./benchmark.json"
        self.activated = False
        self.mutex = Lock()

    def setFilepath(self, filepath):
        self.activated = filepath != ""
        if self.activated:
            logger.info("Activated benchmarking: {}".format(filepath))
        self.filename = filepath

    def write(self):
        self.mutex.acquire()

        try:
            if not self.activated:
                return

            with open(self.filename, "w") as f:
                f.write(json.dumps(self._log))
                logger.info("Written benchmark file: {}".format(self.filename))

        finally:
            self.mutex.release()

    def log(self, text):
        if not self.activated:
            return

        # append is thread-safe (cf. https://stackoverflow.com/questions/6319207/are-lists-thread-safe)
        self._log.append("{}:{}".format(time.time(), text))


# singleton class!
BenchmarkEngine = __BenchmarkEngine()
