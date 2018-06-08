import time


class CryptoHelper:

    def __init__(self):
        pass

    def validate(self, sender, data, signature):
        return True

    def hash(self, json):
        return str(time.time())
