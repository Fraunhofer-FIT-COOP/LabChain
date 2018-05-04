class Transaction:

    def __init__(self, payload):
        self.__payload = payload

    def __init__(self, sender, receiver, payload, signature):
        self.__sender = sender
        self.__receiver = receiver
        self.__payload = payload
        self.__signature = signature

    def get_json(self):
        return self.__payload

    def validate_signature(self):
        return True
