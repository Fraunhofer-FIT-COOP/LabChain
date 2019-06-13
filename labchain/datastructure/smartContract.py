import json
import docker
import time
import os
import socket
import threading
import requests

CONTAINER_IMAGE = "bit_blockchain_image"
DOCKER_FILE_PATH = os.path.join(os.path.dirname(__file__),
                        'dockerResources', 'Dockerfile')
DOCKER_RESOURCES_PATH = os.path.join(os.path.dirname(__file__),
                        'dockerResources')
CONTAINER_TIMEOUT = 10


class SmartContract:

    def __init__(self, id, contract_owners, addresses, code, terminated=False):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        id: Int
            ID of the contract
        addresses : List
            List of all the addresses used by this contract. Starting with the address of the genesis
            transaction of the contract's creation and followed by other transactions that updated the code
            of the contract after it's termination.
        terminated: Bool
            Bool variable that indicates if the contract was terminated or not.
            Default is False.

        Attributes
        ----------
        id: Int
            ID of the contract
        addresses : List
            List of all the addresses used by this contract. Starting with the address of the genesis
            transaction of the contract's creation and followed by other transactions that updated the code
            of the contract after it's termination.
        state : String
            Binary format containing the current state of the contract. 
            It will be used to recover the latest state when the contract is needed.
        terminated: Bool
            Bool variable that indicates if the contract was terminated or not.
            Default is False.
        container: Container object
            Docker container that is used to run the contract's code in a safe and isolated environment.
        port: Int
            Port used to communicate with the container via http requests.
        """

        self._id = id
        self._contract_owners = contract_owners
        self._addresses = addresses
        self._code = code
        self._states = {}
        self._terminated = terminated
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
            self._states = {}

    def restore(self, new_address, new_code):
        """Restarts a terminated contract with a new address.
            The contract is now callable with the old and the new addresses.
        """
        self._addresses.append(new_address)
        self._code = new_code
        self._port = self.find_free_port()
        self._container = self.create_container()
        self._terminated = False

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'id' : self._id,
            'contract_owners' : self._contract_owners,
            'addresses': self._addresses,
            'code': self._code,
            'states': self._states,
            #'container': self._container,
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
        smartContract = SmartContract(data_dict['id'],
                data_dict['contract_owners'],
                data_dict['addresses'],
                data_dict['code'],
                data_dict['terminated'])
        smartContract.states = data_dict['states']
        #smartContract.container = data_dict['container']
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

    # @state.setter
    # def state(self, state):
    #     self._state = state
    
    # def addState(self, state, blockchain_position):
    #     self._states[blockchain_position] = state

    @code.setter
    def code(self, code):
        self._code = code

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
        """Creates a docker container to run the code of the contract."""
        client = docker.from_env()
        try:
            client.images.get(CONTAINER_IMAGE)
        except docker.errors.ImageNotFound:
            print("\nNo image found. Creating image...")
            print(DOCKER_FILE_PATH)
            client.images.build(tag=CONTAINER_IMAGE, path=DOCKER_RESOURCES_PATH, dockerfile=DOCKER_FILE_PATH)
            print("Image created,\n")
        container = client.containers.run(image=str(CONTAINER_IMAGE), ports={"80/tcp": self._port}, detach=True)
        print("Running container\n")

        #Check if the container works
        timeout = time.time() + CONTAINER_TIMEOUT
        url = 'http://localhost:' + str(self._port) + '/'
        while True:
            try:
                r = requests.get(url).json()
                if r == "Container is running" or time.time() > timeout:
                    break
            except:
                continue
        return container

    def find_free_port(self):
        """Returns a free port to be used."""
        s = socket.socket()
        s.bind(('', 0))            # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.

    def get_last_state(self):
        last_state_blockID = max(list(self._states.keys()))
        last_state = self.states[last_state_blockID]
        return last_state

    def add_new_state(self, new_state, blockID):
        self.states[blockID] = new_state

    def remove_states(self, from_blockID):
        new_dict = {}
        for key, value in self._states:
            if key <= from_blockID:
                new_dict[key] = value
        self._states = new_dict
