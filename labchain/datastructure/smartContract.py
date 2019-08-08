import json
import docker
import time
import os
import socket
import requests


CONTAINER_TIMEOUT = 10
CONTAINER_IMAGE = "bit_blockchain_image"
DOCKER_RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'dockerResources')
DOCKER_FILE_PATH = os.path.join(os.path.dirname(__file__),
                        'dockerResources', 'Dockerfile')


class SmartContract:

    def __init__(self, contract_owners, addresses, code, terminated=False):
        """Constructor for SmartContract.

        Parameters
        ----------
        contract_owners: List
            List of all the public addresses that have privileges over this contract. Those privileges
            include terminating and restoring contracts. Contract developers can use this list in their 
            contract logic to restrict some actions to owners only. Contract developers can also leave
            this list empty to create an independent contract that can't be terminated or restored.
        addresses : List
            List of all the addresses used by this contract. Starting with the address of the genesis
            transaction of the contract's creation and followed by other restoration transactions that 
            updated the code of the contract after it's termination.
        code : String
            Binary formated string containing the code of the contract.
        terminated: Bool
            Bool variable that indicates if the contract was terminated or not. Default value is False.

        Attributes
        ----------
        states : Dict
            Dictionary containing the history of states from a contract. The key is the block number where
            the contract's state was updated, the value is a list containing all states changes that took
            place in the block specified in the key ordered in chronological order.
        port: Int
            Port used to communicate with the container via HTTP requests.
        container: Container object
            Docker container that is used to run the contract's code in a safe and isolated environment.
        """

        self._contract_owners = contract_owners
        self._addresses = addresses
        self._terminated = terminated
        self._states = {}
        self._code = code
        self._port = self.find_free_port()
        self._container = self.create_container()

    def terminate(self):
        """Terminates a contract and removes its container."""
        if self._terminated == False:
            self._container.remove(force=True)
            self._container = None
            self._port = None
            self._code = None
            self._terminated = True

    def restore(self, new_address, new_code):
        """Restores a terminated contract with a new address.
            The contract is then callable with the old and the new addresses."""
        self._addresses.append(new_address)
        self._code = new_code
        self._port = self.find_free_port()
        self._container = self.create_container()
        self._terminated = False

    def to_dict(self):
        """Convert own data to a dictionary. The container object is not converted
            since it is not serializable."""
        return {
                'contract_owners' : self._contract_owners,
                'addresses': self._addresses,
                'code': self._code,
                'states': self._states,
                'port': self._port,
                'terminated': self._terminated
                }

    def get_json(self):
        """Serialize this instance to a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a SmartContract instance."""
        data_dict = json.loads(json_data)
        return SmartContract.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a SmartContract from a data dictionary."""
        smartContract = SmartContract(  data_dict['contract_owners'],
                                        data_dict['addresses'],
                                        data_dict['code'],
                                        data_dict['terminated'])
        smartContract.states = data_dict['states']
        smartContract.port = data_dict['port']
        return smartContract

    def __str__(self):
        return str(self.to_dict())

    @property
    def addresses(self):
        return self._addresses

    @property
    def contract_owners(self):
        return self._contract_owners

    @property
    def code(self):
        return self._code

    @property
    def states(self):
        return self._states
    
    @property
    def container(self):
        return self._container

    @property
    def port(self):
        return self._port
    
    @property
    def terminated(self):
        return self._terminated

    @code.setter
    def code(self, code):
        self._code = code

    @states.setter
    def states(self, states):
        self._states = states

    @container.setter
    def container(self, container):
        self._container = container

    @port.setter
    def port(self, port):
        self._port = port

    @addresses.setter
    def addresses(self, addresses):
        self._addresses = addresses

    @contract_owners.setter
    def contract_owners(self, contract_owners):
        self._contract_owners = contract_owners
    
    @terminated.setter
    def terminated(self, terminated):
        self._terminated = terminated

    def create_container(self):
        """Creates a docker container object to run the code of the contract."""
        client = docker.from_env()
        try:
            client.images.get(CONTAINER_IMAGE)
        except docker.errors.ImageNotFound:
            print("\nNo image found. Creating image...")
            print(DOCKER_FILE_PATH)
            client.images.build(tag=CONTAINER_IMAGE, path=DOCKER_RESOURCES_PATH, dockerfile=DOCKER_FILE_PATH)
            print("Image created,\n")
        
        container = client.containers.run(image=str(CONTAINER_IMAGE), ports={"80/tcp": self._port}, detach=True)

        #Check if the container is instantiated before the specified CONTAINER_TIMEOUT
        timeout = time.time() + CONTAINER_TIMEOUT
        url = 'http://localhost:' + str(self._port) + '/'
        while True:
            try:
                r = requests.get(url).json()
                if r == "Container is running" or time.time() > timeout:
                    break
            except:
                if time.time() > timeout:
                    break
                continue
        if time.time() > timeout:
            self._container.remove(force=True)
            return None
        return container

    def find_free_port(self):
        """Returns a free port to be used."""
        s = socket.socket()
        s.bind(('0.0.0.0', 0))            # Bind to a free port provided by the host.
        port = s.getsockname()[1]
        return port

    def get_last_state(self):
        last_state_blockID = max(list(self.states.keys()))
        last_state_list = self.states[last_state_blockID]
        return last_state_list[-1]

    def add_new_state(self, new_state, blockID):
        if self.states.keys().__contains__(blockID):
            self.states[blockID].append(new_state)
        else:
            self.states[blockID] = [new_state]

    def remove_contract_states(self, from_blockID_onwards):
        new_dict = {}
        for key, value in self.states.items():
            if key <= from_blockID_onwards:
                new_dict[key] = value
        self.states = new_dict
