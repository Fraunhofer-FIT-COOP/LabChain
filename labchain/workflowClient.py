import json
import os
from typing import List

from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.util.Menu import Menu
from labchain.util.TransactionFactory import TransactionFactory


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class WorkflowClient:

    def __init__(self, wallet, network_interface, crypto_helper):
        self.network_interface = network_interface
        self.crypto_helper = crypto_helper
        self.wallet = {
            "person1": {
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ3Blc2VFVUo1N2ZjamxVNEQKbW9IdFJlQjhrM3F5Z2lUY0FrY0hqV2VhSXdtaFJBTkNBQVNwUG1oWnRVVDJueXRLV2wrWFgyMVFSdk5pK2dORAplL3lxVzhqb2VMOVhVQTRDbVhhNDZrMmJYT0pnOEZoTjNYRURQRG9Jei9ZQVNoc1JHc0dLWDhsaQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFcVQ1b1diVkU5cDhyU2xwZmwxOXRVRWJ6WXZvRApRM3Y4cWx2STZIaS9WMUFPQXBsMnVPcE5tMXppWVBCWVRkMXhBenc2Q00vMkFFb2JFUnJCaWwvSllnPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            },
            'person2': {
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ2pxY0F2bWptRWk1RExTTnoKbDF0WUcxaS83YzRkQU9zbGxPV0JVL2hMTEJTaFJBTkNBQVNiaUUxYlNmemQzTXdIbFlyY0ZETUdQb09hT1V6VwowamxvRCt3ZU44UlZGdUljZlZta1J5VEJ1QzMreFQ3Qnh6aENkbGJzMk5sZkc3bjNDQkMxRjFPSgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFbTRoTlcwbjgzZHpNQjVXSzNCUXpCajZEbWpsTQoxdEk1YUEvc0hqZkVWUmJpSEgxWnBFY2t3Ymd0L3NVK3djYzRRblpXN05qWlh4dTU5d2dRdFJkVGlRPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            },
            'person3': {
                "private_key": "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ1NKdFQyK1pGLzhRVk5kNlgKU1RiYXk5b3FpQkNrd084anhDbzU3dTJvUWdlaFJBTkNBQVRYT2dsMDRpaVdUN2NtMzR4QUpaV3FreFo5SmxyWAozRjlwNklQOFpLZURMdE9yb1FhYkRyTlRUZWxRNjNvR09RaHdpWlNIdHdJU1o1ZTFKSTd1djF5NgotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0t",
                "public_key": "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFMXpvSmRPSW9sayszSnQrTVFDV1ZxcE1XZlNaYQoxOXhmYWVpRC9HU25neTdUcTZFR213NnpVMDNwVU90NkJqa0ljSW1VaDdjQ0VtZVh0U1NPN3I5Y3VnPT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t"
            }
        }
        self.main_menu = Menu(['Main menu'], {
            '1': ('Send workflow transaction', self.send_dummy_workflow_transaction, []),
            '2': ('Send first task transaction', self.send_dummy_task_transaction, []),
            '3': ('Send subsequent transaction', self.send_dummy_task_transaction2, []),
            '4': ('Check open tasks person 1', self.check_tasks, [self.wallet['person1']['public_key']]),
            '5': ('Check open tasks person 2', self.check_tasks, [self.wallet['person2']['public_key']]),
            '6': ('Check open tasks person 3', self.check_tasks, [self.wallet['person3']['public_key']]),
        }, 'Please select a value: ', 'Exit Workflow Client')

    def main(self):
        """Entry point for the client console application."""
        self.main_menu.show()

    def check_tasks(self, public_key) -> List[TaskTransaction]:
        received = self.network_interface.search_transaction_from_receiver(public_key)
        send = self.network_interface.search_transaction_from_sender(public_key)
        received_task_transaction = [TaskTransaction.from_json(t.get_json()) for t in received if
                                     'workflow_id' in t.payload]
        send_task_transaction = [TaskTransaction.from_json(t.get_json()) for t in send if 'workflow_id' in t.payload]
        send_task_transaction = [t for t in send_task_transaction if t.type == '2']
        received_task_transaction_dict = {self.crypto_helper.hash(t.get_json()): t for t in received_task_transaction}
        send_task_transaction_dict = {t.previous_transaction: t for t in send_task_transaction}
        diff = {k: received_task_transaction_dict[k] for k in set(received_task_transaction_dict)
                - set(send_task_transaction_dict)}
        return [diff[k] for k in diff]

    def send_dummy_workflow_transaction(self):
       
        sender = "person1"
        reciver = "person1"

        process_1 = self.wallet[reciver]["public_key"] + "_1"
        process_2 = self.wallet[reciver]["public_key"] + "_2"

        workflow_transaction_json = {
            "signature": None, 
            "payload": {
                "transaction_type": "1",
                "workflow_id":"0",
                "document": {
                    "strName": "Value1"
                },
                "processes":{},
                "permissions": {}
            }
        }
        workflow_transaction_json["receiver"] = self.wallet[reciver]["public_key"]
        workflow_transaction_json["sender"] = self.wallet[sender]["public_key"]


        workflow_transaction_json["payload"]["in_charge"] = process_1
        workflow_transaction_json["payload"]["processes"][process_1] = [process_2,
                                                                        (self.wallet["person2"]["public_key"] + "_2")]

        workflow_transaction_json["payload"]["permissions"]["strName"] = [process_1, process_2]

        transaction = TransactionFactory.create_transcation(workflow_transaction_json)
        transaction.sign_transaction(self.crypto_helper,  self.wallet[sender]["private_key"])
        self.workflow_transaction_hash = self.crypto_helper.hash(transaction.get_json())
        
        print(workflow_transaction_json)

        self.network_interface.sendTransaction(transaction)

    def send_dummy_task_transaction(self):

        sender = "person1"
        reciver = "person2"

        process_1 = self.wallet[reciver]["public_key"] + "_1"
        process_2 = self.wallet[reciver]["public_key"] + "_2"

        task_transaction_json = {
            "signature": None,
            "payload":{
                "transaction_type": "2",
                "workflow-id":"0",
                "document":{
                    "strName" : "Value2"
                }
            }
        }

        task_transaction_json["payload"]["workflow_transaction"] = self.workflow_transaction_hash
        task_transaction_json["payload"]["previous_transaction"] = self.workflow_transaction_hash

        task_transaction_json["receiver"] = self.wallet[reciver]["public_key"]
        task_transaction_json["sender"] = self.wallet[sender]["public_key"]

        task_transaction_json["payload"]["in_charge"] = process_2

        transaction =TransactionFactory.create_transcation(task_transaction_json)
        transaction.sign_transaction(self.crypto_helper, self.wallet[sender]["private_key"])

        self.task_1_hash = self.crypto_helper.hash(transaction.get_json())

        print(self.task_1_hash)

        self.network_interface.sendTransaction(transaction)

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
        self.network_interface.sendTransaction(transaction)