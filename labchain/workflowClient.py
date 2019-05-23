import os
import json
from collections import OrderedDict

from labchain.network.networking import TransactionDoesNotExistException, BlockDoesNotExistException, BlockDoesNotExistException,NoPeersException
from labchain.datastructure.transaction import Transaction
from labchain.datastructure.taskTransaction import WorkflowTransaction, TaskTransaction
from labchain.datastructure.txpool import TxPool
from labchain.util.cryptoHelper import CryptoHelper
from labchain.util.Menu import Menu

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class WorkflowClient:

    def __init__(self, wallet, network_interface, crypto_helper):
        self.wallet = wallet
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.main_menu = Menu(['Main menu'], {
            '1': ('Send dummy workflow transaction',self.send_dummy_workflow_transaction,[]),
            '2': ('Send dummy task transaction',self.send_dummy_task_transaction,[])
        }, 'Please select a value: ', 'Exit Workflow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def send_dummy_task_transaction(self):

        task_transaction_json = {
            "receiver": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFSWQ2TWtGMEhLQkRIVUthZHlWdDVtYkRzWjhLaApyYVFFOXBPcVowL0NWSEdRS2dhd0ZPL1NQVTF6akdjVE1JeFRKNEFFUkQ4L3V2Y2lNMlFKVzdWbzB3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t",
            "sender": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ0lCVW01RnpJRjF6T1BBa2MKNERxdUU1cWhYeE9KTk0ybmFXTHVRV0NBL0V1aFJBTkNBQVRrU0lyeiswNkJua3FhcjBiTGpsZVVOSEN1ZWR2eAo0ZkxqZms1WmsreTdiSDBOb2Q3SGRYYnZpUmdRQ3ZzczZDMkhMUFRKSzdYV2NSK1FDNTlid3NaKwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
            "signature": None,
            "payload":{
                "workflow-id":"0",
                "document":{
                    "stringAttribute":"1234"
                },
                "in_charge" : "PID_2",
                "next_in_charge": "PID_3",
            }
        }
        transaction = TaskTransaction.from_json(json.dumps(task_transaction_json))
        transaction.sign_transaction(self.crypto_helper, task_transaction_json['sender'])
        self.network_interface.sendTransaction(transaction,2)

    def send_dummy_workflow_transaction(self):

        workflow_transaction_json = {
            "receiver": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ0lCVW01RnpJRjF6T1BBa2MKNERxdUU1cWhYeE9KTk0ybmFXTHVRV0NBL0V1aFJBTkNBQVRrU0lyeiswNkJua3FhcjBiTGpsZVVOSEN1ZWR2eAo0ZkxqZms1WmsreTdiSDBOb2Q3SGRYYnZpUmdRQ3ZzczZDMkhMUFRKSzdYV2NSK1FDNTlid3NaKwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
            "sender": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ0lCVW01RnpJRjF6T1BBa2MKNERxdUU1cWhYeE9KTk0ybmFXTHVRV0NBL0V1aFJBTkNBQVRrU0lyeiswNkJua3FhcjBiTGpsZVVOSEN1ZWR2eAo0ZkxqZms1WmsreTdiSDBOb2Q3SGRYYnZpUmdRQ3ZzczZDMkhMUFRKSzdYV2NSK1FDNTlid3NaKwotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
            "signature": None, 
            "payload":{
                "workflow-id":"0",
                "document":{
                    "stringAttribute":"stringValue",
                    "booleanAttribute": 'true',
                    "integerAttribute" : 1,
                    "floatAttributes": 1.5
                },
                "in_charge" : "PID_0",
                "next_in_charge": "PID_1",
                "processes":{
                    "PID_4" : ["PID_5"],
                    "PID_2" : ["PID_3"],
                    "PID_3" : ["PID_4"],
                    "PID_1" : ["PID_2"]
                },
                "permissions":{
                    "stringAttribute": ["PID_1","PID_2","PID_3"],
                    "booleanAttribute": ["PID_5"],
                    "integerAttribute" : ["PID_4"],
                    "floatAttributes": ["PID_2"]
                }
            }
        }
        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(workflow_transaction_json))
        transaction.sign_transaction(self.crypto_helper, workflow_transaction_json['sender'])
        self.network_interface.sendTransaction(transaction,1)
