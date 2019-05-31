import io
import os
import json
import sys
import unittest

from labchain.datastructure.taskTransaction import TaskTransaction, WorkflowTransaction
from labchain.datastructure.transaction import Transaction
from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.blockchain import BlockChain
from labchain.util.configReader import ConfigReader
from labchain.consensus.consensus import Consensus
from labchain.datastructure.txpool import TxPool


class TransactionTestCase(unittest.TestCase):
    """Class of testcases for the TxPool module"""

    def test_to_dict(self):
        """Test transaction creation from json"""
        json_string = '{"receiver": "r", "signature": "sig", "payload": "1", "sender": "s"}'
        transaction = Transaction.from_json(json_string)
        self.assertTrue(isinstance(transaction, Transaction))
        data_dict = transaction.to_dict()
        self.assertEqual(data_dict['sender'], transaction.sender)
        self.assertEqual(data_dict['receiver'], transaction.receiver)
        self.assertEqual(data_dict['payload'], transaction.payload)
        self.assertEqual(data_dict['signature'], transaction.signature)

    def test_get_json(self):
        """Test json string creation from transaction"""
        transaction = Transaction(sender="s", receiver="r", payload="1", signature="sig")
        self.assertTrue(isinstance(transaction, Transaction))
        json_string = transaction.get_json()
        data_dict = json.loads(json_string)
        self.assertEqual(data_dict['sender'], 's')
        self.assertEqual(data_dict['receiver'], 'r')
        self.assertEqual(data_dict['payload'], '1')
        self.assertEqual(data_dict['signature'], 'sig')

    def test_from_json(self):
        """Test transaction creation from json"""
        json_string = '{"receiver": "r", "signature": "sig", "payload": "1", "sender": "s"}'
        transaction = Transaction.from_json(json_string)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)

    def test_from_dict(self):
        """Test transaction creation from dict"""
        d = {'sender': 's', 'receiver': 'r', 'payload': '1', 'signature': 'sig'}
        transaction = Transaction.from_dict(d)
        self.assertTrue(isinstance(transaction, Transaction))
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)

    def test_sign_transaction(self):
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd' +
                       'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT' +
                       'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl' +
                       'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        my_transaction = Transaction(sender='real_pub_key', receiver="r", payload="1")
        crypto_helper = CryptoHelper.instance()
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        self.assertFalse(my_transaction.signature == "")

    def test_eq_true(self):
        """Test transaction comparison"""
        my_transaction = Transaction(sender="s", receiver="r", payload="1", signature="sig")
        other_transaction = my_transaction
        self.assertTrue(my_transaction.__eq__(other_transaction))

    def test_eq_false(self):
        """Test transaction comparison"""
        my_transaction = Transaction(sender="s", receiver="r", payload="1", signature="sig")
        other_transaction = Transaction(sender=my_transaction.sender, receiver=my_transaction.receiver, payload="2",
                                        signature="othersig")
        self.assertFalse(my_transaction.__eq__(other_transaction))

    def test_validate_transaction_true(self):
        """Test transaction validation"""
        crypto_helper = CryptoHelper.instance()
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd' +
                       'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT' +
                       'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl' +
                       'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        real_pub_key = ('LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowRE' +
                        'FRY0RRZ0FFWnQyeUxvOE0xMWp2bnhXanZqTmQ5RmYxNXpDbApwYXlnSm8zcjBDMlpzNHhRNVR4WmlrcHpua1RHTmFW' +
                        'dGxQWXE4aE1ZaUZiT2hNUmNWK0lISzJ3dU1BPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')
        real_receiver = "test"
        real_payload = "1"
        my_transaction = Transaction(sender=real_pub_key, receiver=real_receiver, payload=real_payload)
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        """"For normal transactions, validation should not need a blockchain"""
        self.assertTrue(my_transaction.validate_transaction(crypto_helper, None))

    def test_validate_transaction_false(self):
        """Test transaction validation"""
        crypto_helper = CryptoHelper.instance()
        real_pr_key = ('LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUd' +
                       'TTTQ5QXdFSEJHMHdhd0lCQVFRZ0c1R3BEREVaUFpsZHh3bEsKOEhvVm9USUJheXhiRFhacFdVV1VoM2szcGNlaFJBT' +
                       'kNBQVJtM2JJdWp3elhXTytmRmFPK00xMzBWL1huTUtXbApyS0FtamV2UUxabXpqRkRsUEZtS1NuT2VSTVkxcFcyVTl' +
                       'pcnlFeGlJVnM2RXhGeFg0Z2NyYkM0dwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t')
        real_pub_key = ('LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowRE' +
                        'FRY0RRZ0FFWnQyeUxvOE0xMWp2bnhXanZqTmQ5RmYxNXpDbApwYXlnSm8zcjBDMlpzNHhRNVR4WmlrcHpua1RHTmFW' +
                        'dGxQWXE4aE1ZaUZiT2hNUmNWK0lISzJ3dU1BPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')
        fake_sender = ('LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFR' +
                       'Y0RRZ0FFSWQ2TWtGMEhLQkRIVUthZHlWdDVtYkRzWjhLaApyYVFFOXBPcVowL0NWSEdRS2dhd0ZPL1NQVTF6akdjVE' +
                       '1JeFRKNEFFUkQ4L3V2Y2lNMlFKVzdWbzB3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t')
        real_payload = "testing fake sender"
        my_transaction = Transaction(sender=fake_sender, receiver=real_pub_key, payload=real_payload)
        my_transaction.sign_transaction(crypto_helper, real_pr_key)
        self.assertFalse(my_transaction.validate_transaction(crypto_helper, None))

    def test_set_signature(self):
        """Test for signature setting"""
        transaction = Transaction(sender="s", receiver="r", payload="1")
        self.assertTrue(isinstance(transaction, Transaction))
        transaction.signature = "sig"
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("sig", transaction.signature)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)
        try:
            transaction.signature = "sg"
            self.assertFalse(True)
        except ValueError:
            self.assertTrue(True)

    def test_set_transaction_hash(self):
        """Test for transaction_hash setting"""
        transaction = Transaction(sender="s", receiver="r", payload="1")
        self.assertTrue(isinstance(transaction, Transaction))
        transaction.transaction_hash = "123"
        self.assertEqual("r", transaction.receiver)
        self.assertEqual("123", transaction.transaction_hash)
        self.assertEqual("1", transaction.payload)
        self.assertEqual("s", transaction.sender)
        try:
            transaction.transaction_hash = "456"
            self.assertFalse(True)
        except ValueError:
            self.assertTrue(True)

    def test_hash(self):
        """Test the __hash__ function, which returns the hash as an integer"""
        transaction = Transaction(sender="s", receiver="r", payload="1")

        transaction.transaction_hash = '0x123456'
        """run int(transaction.transaction_hash, 16) will get the
        integer representation of 0x123456, which is 1193046"""
        # int_hash = int(transaction.transaction_hash, 16)
        int_hash = 1193046
        self.assertEqual(1193046, transaction.__hash__(), msg='{}'.format(transaction.__hash__()))

    def test_print(self):
        """Test printing transaction details"""
        transaction = Transaction(sender="s", receiver="r", payload="1", signature="sig")
        transaction.transaction_hash = "0x123456"
        capturedOutput = io.StringIO()
        temp = sys.stdout
        sys.stdout = capturedOutput
        transaction.print()
        sys.stdout = temp
        self.assertEqual('Sender Address:   s\n' +
                         'Receiver Address: r\n' +
                         'Payload:          1\n' +
                         'Signature:        sig\n' +
                         'Hash:             0x123456\n'
                         , capturedOutput.getvalue())


class TaskTransactionCommon(unittest.TestCase):
    def setUp(self):
        self.init_blockchain();

    def init_blockchain(self):
        self.crypto_helper_obj = CryptoHelper.instance()
        self._txPoolObj = TxPool(self.crypto_helper_obj)
        test_resources_dic_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './resources'))
        test_node_config_file = test_resources_dic_path + '/node_configuration.ini'
        config_reader = ConfigReader(test_node_config_file)

        tolerance = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TOLERANCE_LEVEL')
        pruning = config_reader.get_config(
            section='BLOCK_CHAIN',
            option='TIME_TO_PRUNE')
        min_blocks = config_reader.get_config(
            section='MINING',
            option='NUM_OF_BLOCKS_FOR_DIFFICULTY')

        self.consensus = Consensus()
        self.blockchain_obj = BlockChain(node_id="nodeId1", tolerance_value=tolerance,
                                         pruning_interval=pruning,
                                         consensus_obj=self.consensus,
                                         txpool_obj=self._txPoolObj,
                                         crypto_helper_obj=self.crypto_helper_obj,
                                         min_blocks_for_difficulty=min_blocks,
                                         db=None,
                                         q=None)

    @staticmethod
    def getDummyWorkflowJson(sender_key, receiver_key):
        workflow_transaction_json = {
            "receiver": receiver_key,
            "sender": sender_key,
            "signature": None,
            "payload": {
                "workflow-id": "0",
                "document": {
                    "stringAttribute": "stringValue",
                    "booleanAttribute": 'true',
                    "integerAttribute": 1,
                    "floatAttributes": 1.5
                },
                "in_charge": "PID_1",
                "processes": {
                    "PID_4": ["PID_5"],
                    "PID_2": ["PID_3"],
                    "PID_3": ["PID_4", "PID_6"],
                    "PID_1": ["PID_2"]
                },
                "permissions": {
                    "stringAttribute": ["PID_1", "PID_2", "PID_3"],
                    "booleanAttribute": ["PID_5"],
                    "integerAttribute": ["PID_4"],
                    "floatAttributes": ["PID_2"]
                },
                "previous_transaction": "",
                "workflow_transaction": ""
            }
        }
        return workflow_transaction_json

    @staticmethod
    def getDummyWorkflow(sender_key, receiver_key) -> WorkflowTransaction:
        workflow_transaction_json = WorkflowTransactionTestCase.getDummyWorkflowJson(sender_key, receiver_key)
        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(workflow_transaction_json))
        return transaction

    @staticmethod
    def getDummyTask(sender_key, receiver_key, in_charge, next_in_charge):
        task_transaction_json = {
            "receiver": receiver_key,
            "sender": sender_key,
            "signature": None,
            "payload": {
                "workflow-id": "0",
                "document": {
                    "stringAttribute": "1234"
                },
                "in_charge": in_charge,
                "next_in_charge": next_in_charge,
            }
        }
        return task_transaction_json


class TaskTransactionTestCase(TaskTransactionCommon):

    def test_to_dict(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        task_transaction_json = self.getDummyTask(pu_key1, pu_key2, "PID_2", "PID_3")
        transaction: TaskTransaction = TaskTransaction.from_json(json.dumps(task_transaction_json))
        self.assertTrue(isinstance(transaction, TaskTransaction))
        data_dict = transaction.to_dict()
        self.assertEqual(data_dict['sender'], transaction.sender)
        self.assertEqual(data_dict['receiver'], transaction.receiver)
        self.assertEqual(data_dict['payload'], transaction.payload)
        self.assertEqual(data_dict['signature'], transaction.signature)
        self.assertEqual(data_dict['payload']['document'], transaction.document)
        self.assertEqual(data_dict['payload']['in_charge'], transaction.in_charge)

    def test_permissions_write(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        workflow_transaction_json = self.getDummyWorkflowJson(pu_key1, pu_key2)
        workflowTransaction = WorkflowTransaction.from_json(json.dumps(workflow_transaction_json))

        pr_key3, pu_key3 = self.crypto_helper_obj.generate_key_pair()
        task_transaction_json = self.getDummyTask(pu_key2, pu_key3, "PID_2", "PID_3")
        taskTransaction = TaskTransaction.from_json(json.dumps(task_transaction_json))

        self.assertTrue(taskTransaction._check_permissions_write(workflowTransaction))

    def test_process_definition(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        workflow_transaction_json = self.getDummyWorkflowJson(pu_key1, pu_key2)
        workflowTransaction = WorkflowTransaction.from_json(json.dumps(workflow_transaction_json))

        pr_key3, pu_key3 = self.crypto_helper_obj.generate_key_pair()
        prev_task_transaction_json = self.getDummyTask(pu_key2, pu_key3, "PID_1", "PID_2")
        prev_task_transaction = TaskTransaction.from_json(json.dumps(prev_task_transaction_json))

        pr_key4, pu_key4 = self.crypto_helper_obj.generate_key_pair()
        task_transaction_json = self.getDummyTask(pu_key3, pu_key4, "PID_2", "PID_3")

        taskTransaction = TaskTransaction.from_json(json.dumps(task_transaction_json))

        self.assertTrue(taskTransaction._check_process_definition(workflowTransaction, prev_task_transaction))


class WorkflowTransactionTestCase(TaskTransactionCommon):

    def test_to_dict(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        transaction: WorkflowTransaction = WorkflowTransactionTestCase.getDummyWorkflow(pu_key1, pu_key2)
        self.assertTrue(isinstance(transaction, WorkflowTransaction))
        data_dict = transaction.to_dict()
        self.assertEqual(data_dict['sender'], transaction.sender)
        self.assertEqual(data_dict['receiver'], transaction.receiver)
        self.assertEqual(data_dict['payload'], transaction.payload)
        self.assertEqual(data_dict['signature'], transaction.signature)
        self.assertEqual(data_dict['payload']['document'], transaction.document)
        self.assertEqual(data_dict['payload']['in_charge'], transaction.in_charge)
        self.assertEqual(data_dict['payload']['processes'], transaction.processes)
        self.assertEqual(data_dict['payload']['permissions'], transaction.permissions)

    def test_wrong_in_charge(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        payload['in_charge'] = 'PID_0_1'  # wrong PID format
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_wrong_next_in_charge(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        payload['in_charge'] = 'PID__0'  # wrong PID format
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_wrong_processes_1(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        processes = payload['processes']
        processes['PID_4'] = ['PID_5_']
        payload['processes'] = processes
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_wrong_processes_2(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        processes = payload['processes']
        processes['5_PID'] = ['PID_6']
        payload['processes'] = processes
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_wrong_permissions(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        permissions = payload['permissions']
        permissions['booleanAttribute'] = ['PID 5']
        payload['permissions'] = permissions
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_wrong_permission_attribute(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()
        json_dict = WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        payload = json_dict['payload']
        permissions = payload['permissions']
        permissions['longAttribute'] = ['PID 5']
        payload['permissions'] = permissions
        json_dict['payload'] = payload

        # check that json fields didnt change
        assert set(json_dict.keys()) == set(WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2).keys())

        # check that json values changed
        assert json_dict != WorkflowTransactionTestCase.getDummyWorkflowJson(pu_key1, pu_key2)

        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(json_dict))
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)
        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertFalse(result)

    def test_DummyWorkflow_valid(self):
        pr_key1, pu_key1 = self.crypto_helper_obj.generate_key_pair()
        pr_key2, pu_key2 = self.crypto_helper_obj.generate_key_pair()

        transaction = WorkflowTransactionTestCase.getDummyWorkflow(pu_key1, pu_key2)
        transaction.sign_transaction(self.crypto_helper_obj, pr_key1)

        result = transaction.validate_transaction(CryptoHelper.instance(), self.blockchain_obj)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
