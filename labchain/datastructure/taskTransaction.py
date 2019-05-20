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
        self.previous_transaction = None
        self.workflow_transaction = None

    def validate_transaction(self, crypto_helper):
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :param result: Receive result of transaction validation.
        :return result: True if transaction is valid
        """
        previous_transaction: TaskTransaction = self.previous_transaction
        #import pdb; pdb.set_trace()
        if not isinstance(self, WorkflowTransaction):
            owner_valid = True if previous_transaction.receiver == self.sender else False
            if not self._check_permissions_write():
                logging.debug('Sender has not the permission to write!')
                return False
            if not self._check_process_definition():
                logging.debug('Transaction does not comply to process definition!')
                return False
            if not owner_valid:
                logging.debug('Sender is not the current owner of the document flow!')
                return False
            return super().validate_transaction(crypto_helper)
        else:
            return super().validate_transaction(crypto_helper)

    def _check_permissions_write(self):
        return True
        permission = self.workflow_transaction.permission
        for key in dict:
            if not self.previous_transaction.in_charge in permission[key]:
                return False
        return True

    def _check_process_definition(self):
        return True
        process_definition: Dict = self.workflow_transaction.get_process_definition()
        previous_transaction: TaskTransaction = self.previous_transaction
        in_charge = previous_transaction.in_charge
        possible_receivers = process_definition[in_charge]
        return True if get_pid_of_receiver(self.receiver) in possible_receivers else False  # TODO associate receiver-public-key to corresponding PID

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

    def get_process_definition(self) -> Dict:
        pass  # TODO get process definition

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        return WorkflowTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        return WorkflowTransaction(data_dict['sender'], data_dict['receiver'],
                           data_dict['payload'], data_dict['signature'])
