from __future__ import annotations

import json
from typing import Dict

from labchain.datastructure.transaction import Transaction


class DocumentTransaction(Transaction):

    def __init__(self, sender, receiver, payload, previous_transaction: str):
        super().__init__(sender, receiver, payload)
        self.previous_transaction = previous_transaction
        self.in_charge = 42  # TODO in_charge

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :param result: Receeives result of transaction validation.
        :return result: True if transaction is valid
        """
        previous_transaction: DocumentTransaction = self.get_previous_transaction()
        if previous_transaction is not None:
            owner_valid = True if previous_transaction.receiver == self.sender else False
            return self._check_permissioned_write() \
                   and self._check_process_definition() \
                   and owner_valid and super().validate_transaction(
                crypto_helper)
        else:
            return super().validate_transaction(crypto_helper)

    def _check_permissioned_write(self):
        dict: Dict = json.loads(self.payload)
        permission = self.get_initial_transaction().permission
        for key in dict:
            if not self.get_previous_transaction().in_charge in permission[key]:
                return False
        return True

    def _check_process_definition(self):
        process_definition: Dict = self.get_initial_transaction().get_process_definition()
        previous_transaction: DocumentTransaction = self.get_previous_transaction()
        in_charge = previous_transaction.in_charge
        possible_receivers = process_definition[in_charge]
        return True if get_pid_of_receiver(
            self.receiver) in possible_receivers else False  # TODO associate receiver-public-key to corresponding PID

    """
    Getter for the previous transaction in the workflow
    :return previous_transaction: The DocumentTransaction-Object of the previous transaction, returns None if this is the initial transaction
    """

    def get_previous_transaction(self) -> DocumentTransaction:
        # TODO get previous transaction
        pass

    """
    Getter for the initial transaction in the workflow
    :return initial_transaction: The DocumentTransaxction-Object of the initial transaction
    """

    def get_initial_transaction(self) -> InitialDocumentTransaction:
        # TODO get initial transaction
        pass


class InitialDocumentTransaction(DocumentTransaction):

    def __init__(self, sender, receiver, payload, process: Dict,
                 permission: Dict, previous_transaction=''):
        super().__init__(sender, receiver, payload, previous_transaction)
        self.process = process
        self.permission = permission
        # TODO transaction_type???

    def get_process_definition(self) -> Dict:
        pass  # TODO get process definition
