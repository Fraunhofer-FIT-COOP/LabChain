import logging
import json
import docker
import time
import os
import requests
import logging

from pprint import pformat
from labchain.datastructure.smartContract import SmartContract
from labchain.util.cryptoHelper import CryptoHelper

CONTAINER_NAME = "bit_blockchain_container"
DOCKER_FILES_PATH = os.path.join(os.path.dirname(__file__),
                        'labchain', 'resources',
                        'dockerResources')
CONTAINER_PORT = 5000

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

    def create_container(self):
        client = docker.from_env()

        try:
            client.images.get(CONTAINER_NAME)
        except:
            print("No image found")
            print("Creating image...")
            client.images.build(path=DOCKER_FILES_PATH, tag=CONTAINER_NAME)
            print("Image created")

        container = client.containers.run(image=CONTAINER_NAME, ports={"80/tcp": CONTAINER_PORT}, detach=True)
        print("Running container")
        return container

        # time.sleep(30)
        # container.remove(force=True)
        # print("Quit container")

    def createContract(self, tx):
        container = self.create_container()
        url = "http://localhost:" + CONTAINER_PORT + "/createContract"
        data = {"code": tx.payload['contractCode'],
                "arguments": tx.payload['arguments'],
                "sender": tx.sender}
        r = requests.post(url,json=data).json()
        
        try:
            if(r["success"] == True):
                #TODO UPDATE ADDRESS INFO
                newContract = SmartContract(address=None,
                                            txHash=tx.transaction_hash,
                                            state=r['encodedNewState'])
                newContract.address = self._crypto_helper.hash(newContract.get_json())
                self.addContract(newContract)
            if(r["success"] == False):
                    print(r["error"])
        except:
            logging.error("Contract from transaction " + tx.transaction_hash + 
                        "could not be created")
        container.remove(force=True)

    def callMethod(self, tx, tx_of_contractCreation, state):
        container = self.create_container()
        url = "http://localhost:" + CONTAINER_PORT + "/callMethod"
        data = {"code": tx_of_contractCreation.payload['contractCode'],
                "state": state,
                "methods": tx.payload['methods'],
                "sender": tx.sender}
        r = requests.post(url,json=data).json()

        try:
            if(r["success"] == True):
                self.updateContractState(tx.receiver, r['encodedUpdatedState'])
            if(r["success"] == False):
                print(r["error"])
        except:
            logging.error("Method call from transaction " + tx.transaction_hash + 
                        "could not be completed")
        container.remove(force=True)

    def getState(self, state, tx_of_contractCreation):
        container = self.create_container()
        url = "http://localhost:" + CONTAINER_PORT + "/getState"
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
        container = self.create_container()
        url = "http://localhost:" + CONTAINER_PORT + "/getParameters"
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
        container = self.create_container()
        url = "http://localhost:" + CONTAINER_PORT + "/getMethods"
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