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
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.main_menu = Menu(['Main menu'], {
            '1': ('Send workflow transaction',self.send_dummy_workflow_transaction,[]),
            '2': ('Send first task transaction',self.send_dummy_task_transaction,[]),
            '3': ('Send subsequent transaction',self.send_dummy_task_transaction2,[]),
        }, 'Please select a value: ', 'Exit Workflow Client')
        self.wallet = {
            "person1": {
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ3Blc2VFVUo1N2ZjamxVNEQKbW9IdFJlQjhrM3F5Z2lUY0FrY0hqV2VhSXdtaFJBTkNBQVNwUG1oWnRVVDJueXRLV2wrWFgyMVFSdk5pK2dORAplL3lxVzhqb2VMOVhVQTRDbVhhNDZrMmJYT0pnOEZoTjNYRURQRG9Jei9ZQVNoc1JHc0dLWDhsaQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFcVQ1b1diVkU5cDhyU2xwZmwxOXRVRWJ6WXZvRApRM3Y4cWx2STZIaS9WMUFPQXBsMnVPcE5tMXppWVBCWVRkMXhBenc2Q00vMkFFb2JFUnJCaWwvSllnPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            },
            'person2':{
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ2pxY0F2bWptRWk1RExTTnoKbDF0WUcxaS83YzRkQU9zbGxPV0JVL2hMTEJTaFJBTkNBQVNiaUUxYlNmemQzTXdIbFlyY0ZETUdQb09hT1V6VwowamxvRCt3ZU44UlZGdUljZlZta1J5VEJ1QzMreFQ3Qnh6aENkbGJzMk5sZkc3bjNDQkMxRjFPSgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFbTRoTlcwbjgzZHpNQjVXSzNCUXpCajZEbWpsTQoxdEk1YUEvc0hqZkVWUmJpSEgxWnBFY2t3Ymd0L3NVK3djYzRRblpXN05qWlh4dTU5d2dRdFJkVGlRPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            },
            'person3':{
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ1NKdFQyK1pGLzhRVk5kNlgKU1RiYXk5b3FpQkNrd084anhDbzU3dTJvUWdlaFJBTkNBQVRYT2dsMDRpaVdUN2NtMzR4QUpaV3FreFo5SmxyWAozRjlwNklQOFpLZURMdE9yb1FhYkRyTlRUZWxRNjNvR09RaHdpWlNIdHdJU1o1ZTFKSTd1djF5NgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFMXpvSmRPSW9sayszSnQrTVFDV1ZxcE1XZlNaYQoxOXhmYWVpRC9HU25neTdUcTZFR213NnpVMDNwVU90NkJqa0ljSW1VaDdjQ0VtZVh0U1NPN3I5Y3VnPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            }
        }

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def send_dummy_workflow_transaction(self):
       
        sender = "person1"
        reciver = "person1"

        workflow_transaction_json = {
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
        workflow_transaction_json["receiver"] = self.wallet[reciver]["public_key"]
        workflow_transaction_json["sender"] = self.wallet[sender]["public_key"]
        transaction: WorkflowTransaction = WorkflowTransaction.from_json(json.dumps(workflow_transaction_json))
        transaction.sign_transaction(self.crypto_helper,  self.wallet[sender]["private_key"])
        self.network_interface.sendTransaction(transaction,1)

    def send_dummy_task_transaction(self):

        sender = "person1"
        reciver = "person2"

        task_transaction_json = {
            "signature": None,
            "payload":{
                "workflow-id":"0",
                "document":{
                    "stringAttribute":"1234"
                },
                "in_charge" : "PID_1",
                "next_in_charge": "PID_2",
            }
        }
        task_transaction_json["receiver"] = self.wallet[reciver]["public_key"]
        task_transaction_json["sender"] = self.wallet[sender]["public_key"]
        transaction = TaskTransaction.from_json(json.dumps(task_transaction_json))
        transaction.sign_transaction(self.crypto_helper, self.wallet[sender]["private_key"])
        self.network_interface.sendTransaction(transaction,2)

    def send_dummy_task_transaction2(self):

        sender = "person2"
        reciver = "person3"

        task_transaction_json = {
            "signature": None,
            "payload":{
                "workflow-id":"0",
                "document":{
                    "stringAttribute":"3423423"
                },
                "in_charge" : "PID_2",
                "next_in_charge": "PID_3",
            }
        }
        task_transaction_json["receiver"] = self.wallet[reciver]["public_key"]
        task_transaction_json["sender"] = self.wallet[sender]["public_key"]
        transaction = TaskTransaction.from_json(json.dumps(task_transaction_json))
        transaction.sign_transaction(self.crypto_helper, self.wallet[sender]["private_key"])
        self.network_interface.sendTransaction(transaction,2)

