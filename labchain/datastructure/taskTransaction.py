import json
import logging
from base64 import b64decode
from typing import Dict

from Crypto.PublicKey import ECC

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

        previous_transaction: TaskTransaction = blockchain.get_transaction(self.previous_transaction)[0]
        workflow_transaction: WorkflowTransaction = blockchain.get_transaction(self.workflow_transaction)[0]

        if previous_transaction is None:
            raise ValueError(
                'Corrupted transaction, no previous_transaction found')

        if self.workflow_ID != previous_transaction.workflow_ID:
            logging.warning('Workflow-ID of the new transaction does not match with the previous transaction.')
            return False

        if self.workflow_ID != workflow_transaction.workflow_ID:
            logging.warning('Workflow-ID of the new transaction does not match with the initial transaction.')
            return False

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

        if not self._check_permissions_write(previous_transaction, workflow_transaction):
            logging.warning('Sender has not the permission to write!')
            return False

        if not self._check_process_definition(previous_transaction, workflow_transaction):
            logging.warning(
                'Transaction does not comply to process definition!')
            return False

        # TODO check for duplicate transactions
        return self.validate_transaction_common(crypto_helper, blockchain)

    def validate_transaction_common(self, crypto_helper, blockchain):
        if not self._check_pid_well_formedness(self.in_charge):
            return False
        return super().validate_transaction(crypto_helper, blockchain)

    def _check_permissions_write(self, previous_transaction, workflow_transaction):
        if not workflow_transaction:
            return False
        permissions = workflow_transaction.permissions
        for attributeName in self.document:
            if attributeName not in permissions:
                return False
            if previous_transaction.in_charge not in permissions[attributeName]:
                return False
        return True

    def _check_process_definition(self, previous_transaction, workflow_transaction):
        process_definition = workflow_transaction.processes
        if previous_transaction:
            if self.in_charge not in process_definition[previous_transaction.in_charge]:
                return False
        return True

    def _check_for_duplicate_transactions(self, blockchain):
        parallel_transactions = list(
            set(blockchain.search_transaction_from_sender(self.sender))
            & set(blockchain.search_transaction_to_receiver(self.receiver)))
        parallel_transactions = [t for t in parallel_transactions if
                                 isinstance(t, TaskTransaction) or isinstance(t, WorkflowTransaction)]
        parallel_transactions = [t for t in parallel_transactions if t.workflow_ID == self.workflow_ID]
        parallel_transactions = [t for t in parallel_transactions if
                                 t.previous_transaction == self.previous_transaction]
        return False if len(parallel_transactions) > 0 else True

    def _check_pid_well_formedness(self, PID):
        parts = PID.split(sep='_')
        pid_pubkey = parts[0]
        pid_number = parts[1]

        if not len(parts) == 2:
            return False
        try:
            i = int(pid_number)
        except ValueError:
            logging.warning("Number in PID wrong!")
            logging.debug("Number in PID is: {}".format(parts[1]))
            return False

        decoded_key = ""
        try:
            decoded_key = b64decode(pid_pubkey).decode('utf-8')
            pk = ECC.import_key(decoded_key)  # Get the public key object using public key string
        except TypeError:
            logging.warning("Public Key in PID is wrong!")
            logging.debug("^ Public Key in PID is: {}".format(pid_pubkey))
            return False
        except ValueError:
            logging.warning("Public Key in PID is not a key!")
            logging.debug("^ ------- Public Key in PID is: {}".format(pid_pubkey))
            logging.debug("^ Decoded Public Key in PID is: {}".format(decoded_key))
            return False

        # TODO more rules regarding well-formedness?
        return True

    @property
    def type(self):
        return self.payload['transaction_type']

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
        type = data_dict.get('transaction_type', '0')
        if type == '1':
            return WorkflowTransaction(sender=data_dict['sender'], receiver=data_dict['receiver'],
                                       payload=data_dict['payload'], signature=data_dict['signature'])
        elif type == '2':
            return TaskTransaction(sender=data_dict['sender'], receiver=data_dict['receiver'],
                                   payload=data_dict['payload'], signature=data_dict['signature'])
        else:
            return Transaction(sender=data_dict['sender'], receiver=data_dict['receiver'],
                               payload=data_dict['payload'], signature=data_dict['signature'])


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
            if not self._check_pid_well_formedness(sender):
                return False
            for receiver in receivers:
                if not self._check_pid_well_formedness(receiver):
                    return False
        document_keys = self.document.keys()
        for attr, pids in self.permissions.items():
            for pid in pids:
                if not self._check_pid_well_formedness(pid):
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
