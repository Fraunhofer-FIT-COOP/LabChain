import json
import logging
from typing import Dict

from labchain.datastructure.transaction import Transaction


class TaskTransaction(Transaction):

    def __init__(self, sender, receiver, payload: Dict, signature=None):
        super().__init__(sender, receiver, payload, signature)
        self.payload['transaction_type'] = '2'

    def validate_transaction(self, crypto_helper, blockchain) -> bool:
        """
        Passing the arguments for validation with given public key and signature.
        :param crypto_helper: CryptoHelper object
        :param blockchain: Blockchain object
        :return result: True if transaction is valid
        """
        if self.payload['transaction_type'] is not '2' and self.payload['transaction_type'] is not '1':
            logging.warning('Transaction has wrong transaction type')
            return False

        ""
        previous_transaction = blockchain.get_transaction(self.previous_transaction)
        workflow_transaction = blockchain.get_transaction(self.workflow_transaction)
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
        if not self._check_permissions_write(workflow_transaction):
            logging.warning('Sender has not the permission to write!')
            return False
        if not self._check_process_definition(workflow_transaction, previous_transaction):
            logging.warning(
                'Transaction does not comply to process definition!')
            return False

        # TODO check for duplicate transactions
        return self.validate_transaction_common(crypto_helper, blockchain)

    def validate_transaction_common(self, crypto_helper, blockchain):
        if not self._check_PID_well_formedness(self.in_charge):
            return False
        return super().validate_transaction(crypto_helper, blockchain)

    def _check_permissions_write(self, workflow_transaction):
        if not workflow_transaction:
            return False
        permissions = workflow_transaction.permissions
        for attributeName in self.document:
            if attributeName not in permissions:
                return False
            if self.in_charge not in permissions[attributeName]:
                return False
        return True

    def _check_process_definition(self, workflow_transaction, previous_transaction):
        process_definition = workflow_transaction.processes
        if previous_transaction:
            if self.in_charge not in process_definition[previous_transaction.in_charge]:
                return False
        return True

    def _check_for_wrong_branching(self):
        # TODO implement
        # latest_transaction_hash = getter???
        # if self.transaction_hash == latest_transaction_hash:
        #     return True
        # return False
        pass

    def _check_PID_well_formedness(self, PID):
        parts = PID.split(sep='_')
        if not len(parts) == 2:
            return False
        try:
            i = int(parts[1])
        except ValueError:
            return False
        #TODO more rules regarding well formedness?
        return True

    @property
    def document(self):
        return self.payload['document']

    @property
    def in_charge(self):
        return self.payload['in_charge']

    @property
    def workflow_ID(self):
        return self.payload['workflow-id']

    @property
    def previous_transaction(self):
        return self.payload['previous_transaction']

    @property
    def workflow_transaction(self):
        return self.payload['workflow_transaction']

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
        self.payload['transaction_type'] = '1'

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        return WorkflowTransaction.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        return WorkflowTransaction(data_dict['sender'], data_dict['receiver'],
                                   data_dict['payload'], data_dict['signature'])

    def validate_transaction(self, crypto_helper, blockchain):
        if self.payload['transaction_type'] is not '1':
            logging.warning('Transaction has wrong transaction type')
            return False

        for sender, receivers in self.processes.items():
            if not self._check_PID_well_formedness(sender):
                return False
            for receiver in receivers:
                if not self._check_PID_well_formedness(receiver):
                    return False
        document_keys = self.document.keys()
        for attr, pids in self.permissions.items():
            for pid in pids:
                if not self._check_PID_well_formedness(pid):
                    return False
            if attr not in document_keys:
                return False

        return super().validate_transaction_common(crypto_helper, blockchain)

    @property
    def processes(self):
        return self.payload['processes']

    @property
    def permissions(self):
        return self.payload['permissions']
