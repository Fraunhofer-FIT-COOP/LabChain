import json
import logging
from typing import Dict

from labchain.datastructure.transaction import Transaction


class TaskTransaction(Transaction):

    def __init__(self, sender, receiver, payload, signature = None):
        super().__init__(sender, receiver, payload, signature)
        self.document = payload['document'] # document is a dict
        self.in_charge = payload['in_charge']
        self.next_in_charge = payload['next_in_charge']
        self.workflowID = payload['workflow-id']
        self.previous_transaction = None
        self.workflow_transaction = None

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :param result: Receive result of transaction validation.
        :return result: True if transaction is valid
        """
        if isinstance(self, WorkflowTransaction):
            return super().validate_transaction(crypto_helper)
        previous_transaction = self.previous_transaction
        workflow_transaction = self.workflow_transaction
        if not previous_transaction:
            owner_valid = True if workflow_transaction.receiver == self.sender else False
        else:
            owner_valid = True if previous_transaction.receiver == self.sender else False

        if not owner_valid:
            logging.warning('Sender is not the current owner of the document flow!')
            return False
        if not self._check_permissions_write():
            logging.warning('Sender has not the permission to write!')
            return False
        if not self._check_process_definition():
            logging.warning('Transaction does not comply to process definition!')
            return False
        return super().validate_transaction(crypto_helper)

    def _check_permissions_write(self):
        if not self.workflow_transaction:
            return False
        permissions = self.workflow_transaction.permissions
        for attributeName in self.document:
            if not attributeName in permissions:
                return False
            if not self.in_charge in permissions[attributeName]:
                return False
        return True

    def _check_process_definition(self):
        process_definition = self.workflow_transaction.processes
        if self.previous_transaction:
            if self.in_charge != self.previous_transaction.next_in_charge:
                return False
            if not self.in_charge in process_definition[self.previous_transaction.in_charge]:
                return False
        if not self.next_in_charge in process_definition[self.in_charge]:
            return False
        return True

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Transaction instance."""
        data_dict = json.loads(json_data)
        return TaskTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Transaction from a data dictionary."""
        return TaskTransaction(data_dict['sender'], data_dict['receiver'],
                           data_dict['payload'],data_dict['signature'])

class WorkflowTransaction(TaskTransaction):

    def __init__(self, sender, receiver, payload, signature = None):
        super().__init__(sender, receiver, payload, signature)
        self.processes = payload['processes'] # dict
        self.permissions = payload['permissions'] # dict

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        return WorkflowTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        return WorkflowTransaction(data_dict['sender'], data_dict['receiver'],
                           data_dict['payload'], data_dict['signature'])
