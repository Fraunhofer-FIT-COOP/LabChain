import json


class SmartContract:

    def __init__(self, address, txHash, state):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        address : String
            An internal address used to identify the contract.
        txHash : String
            Instead of storing the contract’s code again in the class we will avoid 
            redundancy by referencing the transaction where it is stored in the blockchain.
        state : String
            Binary format containing the current state of the contract. 
            It will be used to recover the latest state when the contract is needed.

        Attributes
        ----------
        Same as the parameters

        """

        self._address = address
        self._txHash = txHash
        self._state = state

    def to_dict(self):
        """Convert own data to a dictionary."""
        return {
            'address': self._address,
            'txHash': self._txHash,
            'state': self._state
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
        return SmartContract(data_dict['address'], 
                data_dict['txHash'], 
                data_dict['state'])

    def __str__(self):
        return str(self.to_dict())

    @property
    def address(self):
        return self._address

    @property
    def txHash(self):
        return self._txHash

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
