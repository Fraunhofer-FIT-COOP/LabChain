import json
from labchain.singleton import Singleton


class Utility:

    def __init__(self):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        pass

    @staticmethod
    def is_json(object_param):
        try:
            json.loads(object_param)
        except ValueError:
            return False
        return True
