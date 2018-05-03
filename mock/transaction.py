class Transaction:

    def __init__(self, payload):
        self.__payload = payload

    def get_json(self):
        return self.__payload

    def validate_signature(self):
        return True
