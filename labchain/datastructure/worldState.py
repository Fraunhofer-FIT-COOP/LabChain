import logging
import json
import docker
import time
import os
import requests
import logging
import socket

from pprint import pformat
from labchain.datastructure.smartContract import SmartContract
from labchain.util.cryptoHelper import CryptoHelper

CONTAINER_NAME = "bit_blockchain_container"
DOCKER_FILES_PATH = os.path.join(os.path.dirname(__file__),
                        'labchain', 'resources',
                        'dockerResources')

class WorldState:

    def __init__(self, contracts: SmartContract = None):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        contracts: list
            List of smartContracts to be loaded. The default is None.

        Attributes
        ----------
        contracts : list
            List of all the smartContracts in the blockchain.
        _crypto_helper : CryptoHelper
            Instance of the CryptoHelper Module

        """

        if contracts == None:
            self._contracts = []
        else:
            self._contracts = contracts

        self._crypto_helper = CryptoHelper.instance()

    def addContract(self, contract):
        """Adds a contract to the contract list."""
        self._contracts.append(contract)
    
    def updateContractState(self, contractAddress, newState):
        for contract in self._contracts:
            if contract.address == contractAddress:
                contract.state = newState
                break


    def getContract(self, address):
        """Returns the smartContract that has the specified address if it exists."""
        for contract in self._contracts:
            if contract.address == address:
                return contract
        return None


    def to_dict(self):
        """Returns the WorldState data as a dictionary."""
        if len(self._contracts) == 0:
            return {
                'contracts' : []
            }
        c = []
        for contract in self._contracts:
            try:
                c.append(contract.to_dict())
            except Exception as e:
                logging.error("contract error = "+e)
                raise e
        
        return {
            'contracts' : c
        }


    def get_json(self):
        """Returns the WorldState instance as a JSON string."""
        return json.dumps(self.to_dict())


    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a WorldState instance."""
        data_dict = json.loads(json_data)
        return WorldState.from_dict(data_dict)

    
    @staticmethod
    def from_dict(data_dict):
        """Instantiate WorldState from a data dictionary."""
        return WorldState(contracts=[SmartContract.from_dict(contract_dict)
                                   for contract_dict in data_dict['contracts']])


    def __str__(self):
        """String representation of WorldState object"""
        return pformat(self.to_dict())


    def get_computed_hash(self):
        """Gets the hash for the entire WorldState instance"""
        return self._crypto_helper.hash(self.get_json)

    def get_all_contract_addresses(self):
        allAddresses = []
        for contract in self._contracts:
            allAddresses.append(contract.address)
        return allAddresses

    def create_container(self, port):
        client = docker.from_env()

        try:
            client.images.get(CONTAINER_NAME)
        except:
            print("No image found")
            print("Creating image...")
            client.images.build(path=DOCKER_FILES_PATH, tag=CONTAINER_NAME)
            print("Image created")

        container = client.containers.run(image=CONTAINER_NAME, ports={"80/tcp": port}, detach=True)
        print("Running container")
        time.sleep(2)
        return container

        # time.sleep(30)
        # container.remove(force=True)
        # print("Quit container")

    def createContract(self, tx):
        port = self.find_free_port()
        container = self.create_container(port)
        url = "http://localhost:" + str(port) + "/createContract"
        
        try:
            payload = tx.to_dict()['payload'].replace("'",'"')
            payload = json.loads(payload)
            data = {"code": payload['contractCode'],
                    "arguments": payload['arguments'],
                    "sender": tx.sender}
            r = requests.post(url,json=data).json()
            if(r["success"] == True):
                #TODO UPDATE ADDRESS INFO
                txHash = tx.transaction_hash
                if txHash == None:
                    txHash = self._crypto_helper.hash(tx.get_json())
                newContract = SmartContract(address=txHash,
                                            txHash=txHash,
                                            state=r['encodedNewState'])
                #newContract.address = self._crypto_helper.hash(newContract.get_json())
                self.addContract(newContract)
            if(r["success"] == False):
                    print(r["error"])
        except:
            logging.error("Contract from transaction could not be created")
        container.remove(force=True)

    def callMethod(self, tx, tx_of_contractCreation, state):
        port = self.find_free_port()
        container = self.create_container(port)
        url = "http://localhost:" + str(port) + "/callMethod"
        
        payload_contractCreation = tx_of_contractCreation.to_dict()['payload'].replace("'",'"')
        payload = tx.to_dict()['payload'].replace("'",'"')

        data = {"code": json.loads(payload_contractCreation)['contractCode'],
                "state": state,
                "methods": json.loads(payload)['methods'],
                "sender": tx.sender}
        r = requests.post(url,json=data).json()

        try:
            if(r["success"] == True):
                self.updateContractState(tx.receiver, r['encodedUpdatedState'])
                print("Successfully called a method on a contract. New State: " + str(r['encodedUpdatedState']))
            if(r["success"] == False):
                print(r["error"])
        except:
            logging.error("Method call from transaction " + tx.transaction_hash + 
                        "could not be completed")
        container.remove(force=True)

    def getState(self, state, tx_of_contractCreation):
        port = self.find_free_port()
        container = self.create_container(port)
        url = "http://localhost:" + str(port) + "/getState"
        data = {"code": tx_of_contractCreation.payload['contractCode'],
                "state": state}
        r = requests.post(url,json=data).json()

        try:
            if(r["success"] == True):
                return r["state"]
            if(r["success"] == False):
                return r["error"]
        except:
            logging.error("Could not get state")
            return None
        container.remove(force=True)
    

    def getParameters(self, state, methodName, tx_of_contractCreation):
        port = self.find_free_port()
        container = self.create_container(port)
        url = "http://localhost:" + str(port) + "/getParameters"
        data = {"code": tx_of_contractCreation.payload['contractCode'],
                "state": state,
                "methodName": methodName}
        r = requests.post(url,json=data).json()

        try:
            if(r["success"] == True):
                return r["parameters"]
            if(r["success"] == False):
                return r["error"]
        except:
            logging.error("Could not get state")
            return None
        container.remove(force=True)

    def getMethods(self, state, tx_of_contractCreation):
        port = self.find_free_port()
        container = self.create_container(port)
        url = "http://localhost:" + str(port) + "/getMethods"
        data = {"code": tx_of_contractCreation.payload['contractCode'],
                "state": state}
        r = requests.post(url,json=data).json()
        try:
            if(r["success"] == True):
                return r["methods"]
            if(r["success"] == False):
                return r["error"]
        except:
            logging.error("Could not get methods")
            return None
        container.remove(force=True)

    
    def find_free_port(self):
        s = socket.socket()
        s.bind(('', 0))            # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.