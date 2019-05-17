import json
import logging
from typing import Dict
from labchain.datastructure.taskTransaction import TaskTransaction

class WorkflowTransaction(TaskTransaction):

    def __init__(self, sender, receiver, payload):
        super().__init__(sender, receiver, payload)
        self.processes = payload['processes'] # dict
        self.permissions = payload['permissions'] # dict

    def get_process_definition(self) -> Dict:
        pass  # TODO get process definition