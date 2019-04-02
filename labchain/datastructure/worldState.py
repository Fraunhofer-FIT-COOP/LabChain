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
CONTAINER_TIMEOUT = 10

class WorldState:

    def __init__(self):
        """Constructor for WorldState.

        Parameters
        ----------

        Attributes
        ----------
        contracts : list
            List of all the smartContracts in the blockchain.
        _crypto_helper : CryptoHelper
            Instance of the CryptoHelper Module

        """

        self._contracts = []
        self._crypto_helper = CryptoHelper.instance()

    def add_contract(self, contract):
        """Adds a contract to the contract list if it is not already there."""
        for _contract in self._contracts:
            if contract.address == _contract.address:
                break
        self._contracts.append(contract)
    
    def update_contract_state(self, contract_address, new_state):
        for contract in self._contracts:
            if contract.address == contract_address:
                contract.state = new_state
                break


    def get_contract(self, address):
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
                logging.error("contract error = " + e)
                raise e
        
        return {
            'Contracts' : c
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
        """String representation of WorldState object."""
        return pformat(self.to_dict())


    def get_computed_hash(self):
        """Gets the hash for the entire WorldState instance."""
        return self._crypto_helper.hash(self.get_json)

    def get_all_contract_addresses(self):
        """Returns a list of all the contracts stored in worldState."""
        all_addresses = []
        for contract in self._contracts:
            all_addresses.append(contract.address)
        return all_addresses

    def create_container(self, port):
        """Creates a docker container to run the code of the contract."""
        client = docker.from_env()
        try:
            client.images.get(CONTAINER_NAME)
        except:
            print("\nNo image found. Creating image...")
            client.images.build(path=DOCKER_FILES_PATH, )
            print("Image created,\n")
        container = client.containers.run(image=CONTAINER_NAME, ports={"80/tcp": port}, detach=True)
        print("Running container")

        #Check if the container works
        timeout = time.time() + CONTAINER_TIMEOUT
        url = 'http://localhost:' + str(port) + '/'
        while True:
            try:
                r = requests.get(url).json()
                if r == "Container is running" or time.time() > timeout:
                    break
            except:
                continue
        return container

    def create_contract(self, tx):
        """Creates a new contract and adds it to the list _contracts."""
        port = self.find_free_port()
        container = self.create_container(port)
        url = 'http://localhost:' + str(port) + '/createContract'
        try:
            payload = tx.to_dict()['payload'].replace("'",'"')
            payload = json.loads(payload)
            data = {'code': payload['contractCode'],
                    'arguments': payload['arguments'],
                    'sender': tx.sender}
            r = requests.post(url,json=data).json()
            if(r['success'] == True):
                txHash = tx.transaction_hash
                if txHash == None:
                    txHash = self._crypto_helper.hash(tx.get_json())
                new_contract = SmartContract(address=txHash,
                                            txHash=txHash,
                                            state=r['encodedNewState'])
                self.add_contract(new_contract)
            if(r['success'] == False):
                    print(r['error'])
        except:
            logging.error('Contract from transaction could not be created')
        container.remove(force=True)

    def call_method(self, tx, tx_of_contractCreation, state):
        """Calls a method or methods on an existing contract from the _contracts list."""
        port = self.find_free_port()
        container = self.create_container(port)
        url = 'http://localhost:' + str(port) + '/callMethod'
        
        payload_contractCreation = tx_of_contractCreation.to_dict()['payload'].replace("'",'"')
        payload = tx.to_dict()['payload'].replace("'",'"')

        data = {'code': json.loads(payload_contractCreation)['contractCode'],
                'state': state,
                'methods': json.loads(payload)['methods'],
                'sender': tx.sender}
        r = requests.post(url,json=data).json()

        try:
            if(r['success'] == True):
                self.update_contract_state(tx.receiver, r['encodedUpdatedState'])
            if(r["success"] == False):
                print(r["error"])
        except:
            logging.error('Method call from transaction ' + tx.transaction_hash + 
                        'could not be completed')
        container.remove(force=True)

    def get_state(self, state, tx_of_contractCreation):
        """Returns a readable version of the current state of a contract
            Note: This only works if the contract has a to_dict method."""
        port = self.find_free_port()
        container = self.create_container(port)
        url = 'http://localhost:' + str(port) + '/getState'

        payload_contractCreation = tx_of_contractCreation.to_dict()['payload'].replace("'",'"')

        data = {'code': json.loads(payload_contractCreation)['contractCode'],
                'state': state}
        r = requests.post(url,json=data).json()
        print(r)
        try:
            if(r['success'] == True):
                return r['state']
            if(r['success'] == False):
                return r['error']
        except:
            logging.error('Could not get state')
            return None
        container.remove(force=True)
    

    def get_parameters(self, state, methodName, tx_of_contractCreation):
        """Returns the parameters that a contract constructor/method needs to execute."""
        port = self.find_free_port()
        container = self.create_container(port)
        url = 'http://localhost:' + str(port) + '/getParameters'
        data = {'code': tx_of_contractCreation.to_dict()['payload']['contractCode'],
                'state': state,
                'methodName': methodName}
        r = requests.post(url,json=data).json()

        try:
            if(r['success'] == True):
                return r['parameters']
            if(r['success'] == False):
                return r["error"]
        except:
            logging.error('Could not get parameters')
            return None
        container.remove(force=True)

    def get_methods(self, state, tx_of_contractCreation):
        """Returns the methods that a contract has."""
        port = self.find_free_port()
        container = self.create_container(port)
        url = 'http://localhost:' + str(port) + '/getMethods'

        payload = json.loads(tx_of_contractCreation['payload'].replace("'",'"'))

        data = {'code': payload['contractCode'],
                'state': state}
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                return r['methods']
            if(r["success"] == False):
                return r['error']
        except:
            logging.error('Could not get methods')
            return None
        container.remove(force=True)

    
    def find_free_port(self):
        """Returns a free port to be used."""
        s = socket.socket()
        s.bind(('', 0))            # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.