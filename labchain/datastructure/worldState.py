import logging
import json
import docker
import time
import os

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

        self._crypto_helper = CryptoHelper()

    
    def addContract(self, contract):
        """Adds a contract to the contract list."""
        self._contracts.append(contract)


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


    def create_container(self):
        client = docker.from_env()

        try:
            client.images.get(CONTAINER_NAME)
        except:
            print("No image found")
            print("Creating image...")
            client.images.build(path=DOCKER_FILES_PATH, tag=CONTAINER_NAME)
            print("Image created")

        container = client.containers.run(image=CONTAINER_NAME, ports={"80/tcp": 5000}, detach=True)
        print(container)
        print("Running container")

        time.sleep(30)
        container.remove(force=True)
        print("Quit container")