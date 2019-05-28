import json
import logging
from typing import Dict

from labchain.datastructure.transaction import Transaction


class TaskTransaction(Transaction):

    def __init__(self, sender, receiver, payload: Dict, signature=None):
        super().__init__(sender, receiver, payload, signature)
        self.document: Dict = payload['document']
        self.in_charge: str = payload['in_charge']
        self.next_in_charge = payload['next_in_charge']
        self.workflowID = payload['workflow-id']
        self.previous_transaction = None
        self.workflow_transaction = None
        self.payload['transaction_type'] = '2'

    def validate_transaction(self, crypto_helper) -> bool:
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :return result: True if transaction is valid
        """
        if isinstance(self, WorkflowTransaction):
            return super().validate_transaction(crypto_helper)
        # IMO we need access to the blockchain here, or at least to the networking_getters
        previous_transaction: TaskTransaction = self.previous_transaction  # No idea what group-3 is thinking here
        workflow_transaction: WorkflowTransaction = self.workflow_transaction  # No idea what group-3 is thinking here
        if previous_transaction is None:
            raise ValueError(
                'Corrupted transaction, no previous_transaction found')

        if not previous_transaction.receiver == self.sender:
            logging.warning(
                'Sender is not the receiver of the previous transaction!')
            return False
        if not previous_transaction.in_charge.split(sep='_')[0] == self.sender:
            logging.warning(
                'Sender is not the current owner of the document flow!')
            return False
        if not self.in_charge.split(sep='_')[0] == self.receiver:
            logging.warning('Receiver does not correspond to in_charge flag')
            return False
        if not self._check_permissions_write():
            logging.warning('Sender has not the permission to write!')
            return False
        if not self._check_process_definition():
            logging.warning(
                'Transaction does not comply to process definition!')
            return False

        # TODO check for duplicate transactions

        return super().validate_transaction(crypto_helper)

    def _check_permissions_write(self):
        if not self.workflow_transaction:
            return False
        permissions = self.workflow_transaction.permissions
        for attributeName in self.document:
            if attributeName not in permissions:
                return False
            if self.in_charge not in permissions[attributeName]:
                return False
        return True

    def _check_process_definition(self):
        process_definition = self.workflow_transaction.processes
        if self.previous_transaction:
            if self.in_charge != self.previous_transaction.next_in_charge:
                return False
            if self.in_charge not in process_definition[
                self.previous_transaction.in_charge]:
                return False
        if self.next_in_charge not in process_definition[self.in_charge]:
            return False
        return True

    def _check_for_wrong_branching(self):
        # TODO implement
        # latest_transaction_hash = getter???
        # if self.transaction_hash == latest_transaction_hash:
        #     return True
        # return False
        pass

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Transaction instance."""
        data_dict = json.loads(json_data)
        return TaskTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Transaction from a data dictionary."""
        return TaskTransaction(data_dict['sender'], data_dict['receiver'],
                               data_dict['payload'], data_dict['signature'])


class WorkflowTransaction(TaskTransaction):

    def __init__(self, sender, receiver, payload: Dict, signature=None):
        super().__init__(sender, receiver, payload, signature)
        self.processes: Dict = payload['processes']
        self.permissions: Dict = payload['permissions']
        self.payload['transaction_type'] = '1'

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        return WorkflowTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        return WorkflowTransaction(data_dict['sender'], data_dict['receiver'],
                                   data_dict['payload'], data_dict['signature'])

    def validate_transaction(self, crypto_helper):
        # TODO angeblich sollen wir hier was validieren, aber was eigentlich?
        return super().validate_transaction(crypto_helper)
