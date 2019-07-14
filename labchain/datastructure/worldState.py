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
        _contract_list : List
            List of all active smartContract objects in the blockchain (also terminated).
        _crypto_helper : CryptoHelper
            Instance of the CryptoHelper Module
        """

        self._contract_list = []
        self._crypto_helper = CryptoHelper.instance()


    def get_contract(self, contract_address):
        """Returns the smartContract that has the specified address if it exists."""
        for contract in self._contract_list:
            for address in contract.addresses:
                if address == contract_address:
                    return contract
        return None

    def terminate_contract(self, contract_address, sender):
        """Terminates the smartContract that has the specified address if it exists."""
        for contract in self._contract_list:
            if contract_address in contract.addresses:
                if sender in contract.contract_owners:
                    contract.terminate()
                    return True
        return False
    
    def restore_contract(self, tx, blockID):
        """Restores the smartContract that has the specified address if it exists."""
        contract_address = tx.receiver
        sender = tx.sender
        payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))
        new_code = payload['contractCode']
        new_address = tx.transaction_hash
        if new_address == None:
            new_address = self._crypto_helper.hash(tx.get_json())
        
        #Inject sender at the beginning of the arguments
        arguments = json.dumps(payload['arguments'])
        arguments = arguments.replace('{','{"sender": "' + tx.sender + '", ', 1)
        arguments = json.loads(arguments)
        
        for contract in self._contract_list:
            if contract_address in contract.addresses:
                if sender in contract.contract_owners:
                    try:
                        contract.restore(new_address,new_code)
                        url = 'http://localhost:' + str(contract.port) + '/createContract'
                        data = {'sender': tx.sender,
                                'code': payload['contractCode'],
                                'contract_file_name': payload['contract_file_name'],
                                'arguments': arguments}
                        r = requests.post(url,json=data).json()
                        if(r['success'] == True):
                            new_state = r['encodedNewState']
                            contract.add_new_state(new_state, blockID)
                        if(r['success'] == False):
                                print(r['error'])
                    except:
                        logging.error('Contract from transaction could not be restored')

    def update_contract_state(self, contract_address, new_state, new_encoded_state, blockID):
        """Adds a new state to the state history of a contract."""
        contract = self.get_contract(contract_address)
        if contract:
            contract.contract_owners = new_state['contract_owners']
            contract.add_new_state(new_encoded_state, blockID)
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


    def create_contract(self, tx, blockID):
        """Creates a new contract and adds it to the contract_list."""
        payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))
        txHash = tx.transaction_hash
        if txHash == None:
            txHash = self._crypto_helper.hash(tx.get_json())
        
        contract_owners = [tx.sender]
        contract_addresses = [txHash]
        contract_code = payload['contractCode']
        contract = SmartContract(contract_owners, contract_addresses, contract_code)

        url = 'http://localhost:' + str(contract.port) + '/createContract'
        try:
            #Inject sender at the beginning of the arguments
            arguments = json.dumps(payload['arguments'])
            arguments = arguments.replace('{','{"sender": "' + tx.sender + '", ', 1)
            arguments = json.loads(arguments)

            data = {'sender': tx.sender,
                    'code': payload['contractCode'],
                    'contract_file_name': payload['contract_file_name'],
                    'arguments': arguments
                    }
            r = requests.post(url,json=data).json()
            if(r['success'] == True):
                contract.states[blockID] = [r['encodedNewState']]
                self._contract_list.append(contract)
            if(r['success'] == False):
                    print(r['error'])
        except:
            logging.error('Contract from transaction could not be created')


    def call_method(self, tx, blockID):
        """Calls a method or methods on an existing contract from the _contract_list."""
        contract = self.get_contract(tx.to_dict()['receiver'])
        url = 'http://localhost:' + str(contract.port) + '/callMethod'

        payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))

        data = {'code': contract.code,
                'state': contract.get_last_state(),
                'contract_file_name': payload['contract_file_name'],
                'methods': payload['methods'],
                'sender': tx.sender}
        
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                self.update_contract_state(tx.receiver, r['updatedState'], r['encodedUpdatedState'], blockID)
            if(r["success"] == False):
                print(r["error"])
        except:
            print('Method call from transaction could not be completed')


    def get_state(self, contract_address):
        """Returns a readable version of the current state of a contract
            Note: This only works if the contract has a to_dict method."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getState'

        data = {'code': contract.code,
                'state': contract.get_last_state()}
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                response = r['state']
                response['addresses'] = contract.addresses
                return response
            if(r['success'] == False):
                return r['error']
        except:
            logging.error('Could not get readable state from contract.')
            return None


    def get_parameters(self, contract_address, methodName):
        """Returns the parameters that a contract constructor/method needs to execute."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getParameters'
        data = {'code': contract.code,
                'state': contract.get_last_state(),
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


    def get_methods(self, contract_address):
        """Returns the methods that a contract has."""
        contract = self.get_contract(contract_address)
        url = 'http://localhost:' + str(contract.port) + '/getMethods'

        data = {'code': contract.code,
                'state': contract.get_last_state()}
        r = requests.post(url,json=data).json()
        try:
            if(r['success'] == True):
                return r['methods']
            if(r["success"] == False):
                return r['error']
        except:
            logging.error('Could not get methods from contract with id: ' + str(contract.id))
            return None


    def remove_contract_states(self, from_blockID_onwards):
        for contract in self._contract_list:
            contract.remove_contract_states(from_blockID_onwards)
            if contract.states == {}:
                contract.terminate()
                self._contract_list.remove(contract)