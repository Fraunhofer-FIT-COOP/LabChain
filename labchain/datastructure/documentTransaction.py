import json

from labchain.datastructure.transaction import Transaction


class DocumentTransaction(Transaction):

    def __init__(self, sender, receiver, payload):
        super().__init__(sender, receiver, payload)
        pass

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param public_key: Public key of the signer in the string format.
        :param payload: JSON of the data to be signed.
        :param result: Receeives result of transaction validation.
        """
        data = json.dumps({
            'sender': self.__sender,
            'receiver': self.__receiver,
            'payload': self.__payload
        })
        return crypto_helper.validate(self.sender, data, self.signature)