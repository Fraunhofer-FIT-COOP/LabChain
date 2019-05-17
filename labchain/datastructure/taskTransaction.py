import json
import logging
from typing import Dict

from labchain.datastructure.transaction import Transaction


class TaskTransaction(Transaction):

    def __init__(self, sender, receiver, payload):
        super().__init__(sender, receiver, payload)
        self.document = payload['document'] # document is a dict
        self.in_charge = payload['in_charge']

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :param result: Receive result of transaction validation.
        :return result: True if transaction is valid
        """
        previous_transaction: TaskTransaction = None # self.get_previous_transaction()
        if not isinstance(self, WorkflowTransaction):
            owner_valid = True if previous_transaction.receiver == self.sender else False
            if not self._check_permissions_write():
                logging.debug('Sender has not the permission to write!')
                return False
            if not self._check_process_definition():
                logging.debug(
                    'Transaction does not comply to process definition!')
                return False
            if not owner_valid:
                logging.debug(
                    'Sender is not the current owner of the document flow!')
                return False
            return super().validate_transaction(crypto_helper)
        else:
            return super().validate_transaction(crypto_helper)

    def _check_permissions_write(self):
        dict: Dict = json.loads(self.payload)
        permission = self.get_workflow_transaction().permission
        for key in dict:
            if not self.get_previous_transaction().in_charge in permission[key]:
                return False
        return True

    def _check_process_definition(self):
        process_definition: Dict = self.get_workflow_transaction().get_process_definition()
        previous_transaction: TaskTransaction = self.get_previous_transaction()
        in_charge = previous_transaction.in_charge
        possible_receivers = process_definition[in_charge]
        return True if get_pid_of_receiver(self.receiver) in possible_receivers else False  # TODO associate receiver-public-key to corresponding PID

    """
    Getter for the previous transaction in the workflow
    :return previous_transaction: The TaskTransaction-Object of the previous transaction, returns None if this is the initial transaction
    """

    """
    Getter for the initial transaction in the workflow
    :return initial_transaction: The DocumentTransaxction-Object of the initial transaction
    """
