import json
import requests
import logging

from pprint import pformat
from labchain.datastructure.smartContract import SmartContract
from labchain.util.cryptoHelper import CryptoHelper

class WorldState:

    def __init__(self):
        """Constructor for WorldState.

        Parameters
        ----------

        Attributes
        ----------
        contract_list : List
            List of all the smartContracts in the blockchain.
        _crypto_helper : CryptoHelper
            Instance of the CryptoHelper Module

        """

        self._contract_list = []
        self._contract_id_counter = 0
        self._crypto_helper = CryptoHelper.instance()


    def get_contract(self, contract_address):
        """Returns the smartContract that has the specified address if it exists."""
        for contract in self._contract_list:
            for address in contract.addresses:
                if address == contract_address:
                    return contract
        return None


    def update_contract_state(self, contract_address, new_state):
        """Updates the state of a contract."""
        contract = self.get_contract(contract_address)
        if contract:
            contract.state = new_state
            return True
        else:
            return False


    def to_dict(self):
        """Returns the WorldState data as a dictionary."""
        if len(self._contract_list) == 0:
            return {
                'contract_list' : []
            }
        c = []
        for contract in self._contract_list:
            try:
                c.append(contract.to_dict())
            except Exception as e:
                logging.error("contract error = " + e)
                raise e
        return {
            'contract_list' : c
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
        worldState = WorldState
        worldState.contract_list = [SmartContract.from_dict(contract_dict)
                                   for contract_dict in data_dict['contract_list']]
        return worldState


    def __str__(self):
        """String representation of WorldState object."""
        return pformat(self.to_dict())


    def get_computed_hash(self):
        """Gets the hash for the entire WorldState instance."""
        return self._crypto_helper.hash(self.get_json)

    def get_all_contract_addresses(self):
        """Returns a list of all the contract addresses stored in worldState."""
        all_addresses = []
        for contract in self._contract_list:
            for address in contract.addresses:
                all_addresses.append(address)
        return all_addresses


    def create_contract(self, tx):
        """Creates a new contract and adds it to the contract_list."""
        payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))
        contract = SmartContract(self._contract_id_counter, [tx.sender], payload['contractCode'])
        self._contract_id_counter += 1
        url = 'http://localhost:' + str(contract.port) + '/createContract'
        try:
            data = {'code': payload['contractCode'],
                    'arguments': payload['arguments'],
                    'sender': tx.sender}
            r = requests.post(url,json=data).json()
            if(r['success'] == True):
                contract.state = r['encodedNewState']
                self.contract_list.append(contract)
            if(r['success'] == False):
                    print(r['error'])
        except:
            logging.error('Contract from transaction could not be created')


        # """Creates a new contract and adds it to the list _contracts."""
        # port = self.find_free_port()
        # container = self.create_container(port)
        # url = 'http://localhost:' + str(port) + '/createContract'
        # try:
        #     payload = tx.to_dict()['payload'].replace("'",'"')
        #     payload = json.loads(payload)
        #     data = {'code': payload['contractCode'],
        #             'arguments': payload['arguments'],
        #             'sender': tx.sender}
        #     r = requests.post(url,json=data).json()
        #     if(r['success'] == True):
        #         txHash = tx.transaction_hash
        #         if txHash == None:
        #             txHash = self._crypto_helper.hash(tx.get_json())
        #         new_contract = SmartContract(address=txHash,
        #                                     txHash=txHash,
        #                                     state=r['encodedNewState'])
        #         self.add_contract(new_contract)
        #     if(r['success'] == False):
        #             print(r['error'])
        # except:
        #     logging.error('Contract from transaction could not be created')
        # container.remove(force=True)


    def call_method(self, tx):
        """Calls a method or methods on an existing contract from the _contract_list."""
        contract = self.get_contract(tx.to_dict()['receiver'])
        url = 'http://localhost:' + str(contract.port) + '/callMethod'

        payload = tx.to_dict()['payload'].replace("'",'"')

        data = {'code': contract.code,
                'state': contract.state,
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


        # """Calls a method or methods on an existing contract from the _contract_list."""
        # port = self.find_free_port()
        # container = self.create_container(port)
        # url = 'http://localhost:' + str(port) + '/callMethod'
        
        # payload_contractCreation = tx_of_contractCreation.to_dict()['payload'].replace("'",'"')
        # payload = tx.to_dict()['payload'].replace("'",'"')

        # data = {'code': json.loads(payload_contractCreation)['contractCode'],
        #         'state': state,
        #         'methods': json.loads(payload)['methods'],
        #         'sender': tx.sender}
        # r = requests.post(url,json=data).json()

        # try:
        #     if(r['success'] == True):
        #         self.update_contract_state(tx.receiver, r['encodedUpdatedState'])
        #     if(r["success"] == False):
        #         print(r["error"])
        # except:
        #     logging.error('Method call from transaction ' + tx.transaction_hash + 
        #                 'could not be completed')
        # container.remove(force=True)

    def get_state(self, contract_address):
        """Returns a readable version of the current state of a contract
            Note: This only works if the contract has a to_dict method."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getState'

        data = {'code': contract.code,
                'state': contract.state}
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                return r['state']
            if(r['success'] == False):
                return r['error']
        except:
            logging.error('Could not get readable state from contract with id: ' + str(contract.id))
            return None


    def get_parameters(self, contract_address, methodName):
        """Returns the parameters that a contract constructor/method needs to execute."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getParameters'
        data = {'code': contract.code,
                'state': contract.state,
                'methodName': methodName}
        r = requests.post(url,json=data).json()

        try:
            if(r['success'] == True):
                return r['parameters']
            if(r['success'] == False):
                return r["error"]
        except:
            logging.error('Could not get parameters from contract with id: ' + str(contract.id))
            return None



        # """Returns the parameters that a contract constructor/method needs to execute."""
        # port = self.find_free_port()
        # container = self.create_container(port)
        # url = 'http://localhost:' + str(port) + '/getParameters'
        # data = {'code': tx_of_contractCreation.to_dict()['payload']['contractCode'],
        #         'state': state,
        #         'methodName': methodName}
        # r = requests.post(url,json=data).json()

        # try:
        #     if(r['success'] == True):
        #         return r['parameters']
        #     if(r['success'] == False):
        #         return r["error"]
        # except:
        #     logging.error('Could not get parameters')
        #     return None
        # container.remove(force=True)

    def get_methods(self, contract_address):
        """Returns the methods that a contract has."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getMethods'

        data = {'code': contract.code,
                'state': contract.state}
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                return r['methods']
            if(r["success"] == False):
                return r['error']
        except:
            logging.error('Could not get methods from contract with id: ' + str(contract.id))
            return None



        # """Returns the methods that a contract has."""
        # port = self.find_free_port()
        # container = self.create_container(port)
        # url = 'http://localhost:' + str(port) + '/getMethods'

        # payload = json.loads(tx_of_contractCreation['payload'].replace("'",'"'))

        # data = {'code': payload['contractCode'],
        #         'state': state}
        # r = requests.post(url,json=data).json()
        # try:
        #     if(r['success'] == True):
        #         return r['methods']
        #     if(r["success"] == False):
        #         return r['error']
        # except:
        #     logging.error('Could not get methods')
        #     return None
        # container.remove(force=True)
