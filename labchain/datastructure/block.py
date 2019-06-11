from hashlib import sha256 as sha
import json
import logging
from pprint import pformat
import time
import requests

from labchain.util.cryptoHelper import CryptoHelper
from labchain.datastructure.transaction import Transaction, Transaction_Types
from labchain.datastructure.smartContract import SmartContract


class Block(object):
    def __init__(self, block_id=None, merkle_tree_root=None,
                 predecessor_hash=None, block_creator_id=None,
                 transactions=[], nonce=0, timestamp=time.time(),
                 difficulty=-1):
        """Constructor for Block, placeholder for Block information.

        Parameters
        ----------
        block_id : Int
            ID of the block
        merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        predecessor_hash : Hash
            Hash of the predecessor block to this block
        block_creator_id : String
            ID of the node who created this block
        transactions : List
            Transactions to be included in the block
        nonce : Int
            Value for which block hash satisfies criteria of HashCash
        timestamp : Timestamp of the block creation
        difficulty: Int
            Difficulty value used for the block mining

        Attributes
        ----------
        Same as the parameters

        """
        self._block_id = block_id
        self._timestamp = timestamp
        self._transactions = transactions
        self._merkle_tree_root = merkle_tree_root
        self._predecessor_hash = predecessor_hash
        self._nonce = nonce
        self._block_creator_id = block_creator_id
        self._difficulty = difficulty
        self._logger = logging.getLogger(__name__)

    def to_dict(self):
        """Returns block data as a dictionary."""
        if self._transactions is None:
            return {
                'nr': self._block_id,
                'timestamp': self._timestamp,
                'merkleHash': self._merkle_tree_root,
                'predecessorBlock': self._predecessor_hash,
                'nonce': self._nonce,
                'creator': self._block_creator_id,
                'transactions': [],
                'difficulty': self._difficulty
            }
        t = []
        for transaction in self._transactions:
            try:
                t.append(transaction.to_dict())
            except Exception as e:
                logging.error("tx error = "+e)
                raise e

        return {
            'nr': self._block_id,
            'timestamp': self._timestamp,
            'merkleHash': self._merkle_tree_root,
            'predecessorBlock': self._predecessor_hash,
            'nonce': self._nonce,
            'creator': self._block_creator_id,
            'transactions': t,
            'difficulty': self._difficulty
        }

    def to_json_headers(self):
        """Returns block headers data as JSON"""
        return json.dumps({'nr': self._block_id,
                           'merkleHash': self._merkle_tree_root,
                           'predecessorBlock': self._predecessor_hash,
                           'nonce': self._nonce,
                           'creator': self._block_creator_id,
                           'difficulty': self._difficulty})

    def get_json(self):
        """Returns this Block instance as a JSON string."""
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Block instance."""
        data_dict = json.loads(json_data)
        return Block.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict):
        """Instantiate a Block from a data dictionary."""
        return Block(block_id=data_dict['nr'],
                     merkle_tree_root=data_dict['merkleHash'],
                     predecessor_hash=data_dict['predecessorBlock'],
                     block_creator_id=data_dict['creator'],
                     transactions=[Transaction.from_dict(transaction_dict)
                                   for transaction_dict in data_dict['transactions']],
                     nonce=data_dict['nonce'],
                     timestamp=data_dict['timestamp'],
                     difficulty=data_dict['difficulty'])

    def __str__(self):
        """String representation of Block object"""
        return pformat(self.to_dict())

    @property
    def block_id(self):
        return self._block_id

    @property
    def merkle_tree_root(self):
        return self._merkle_tree_root

    @property
    def predecessor_hash(self):
        return self._predecessor_hash

    @property
    def block_creator_id(self):
        return self._block_creator_id

    @property
    def transactions(self):
        return self._transactions

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def nonce(self):
        return self._nonce

    @nonce.setter
    def nonce(self, nonce):
        self._nonce = nonce

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, difficulty):
        if self._difficulty < 1:
            self._difficulty = difficulty

    def __eq__(self, other):
        """Compare this block fields with other block"""
        if isinstance(other, Block) or isinstance(other, LogicalBlock):
            return all([self._block_id == other.block_id,
                        self._timestamp == other.timestamp,
                        self._transactions == other.transactions,
                        self._merkle_tree_root == other.merkle_tree_root,
                        self._predecessor_hash == other.predecessor_hash,
                        self._nonce == other.nonce,
                        self._block_creator_id == other.block_creator_id,
                        self._difficulty == other._difficulty])
        else:
            return False

    def mine_equality(self, other):
        """Compare whether two blocks are considered equal wrt Mining
        Returns True if either the block ID of the two blocks matches
                        or any of the transactions in the transaction set
                        matches with others' transaction set.
        Else returns False
        """
        if isinstance(other, Block) or isinstance(other, LogicalBlock):
            return any([self._block_id == other.block_id,
                        any(t in self._transactions for t in other.transactions)])


class LogicalBlock(Block):
    def __init__(self, block_id=None, transactions=[], predecessor_hash=None,
                 block_creator_id=None, merkle_tree_root=None, nonce=0,
                 timestamp=time.time(), consensus_obj=None, difficulty=-1):
        """Constructor for LogicalBlock, derives properties from the
        placeholder class Block.

        Parameters
        ----------
        block_id : Int
            ID of the block
        transactions : List
            Transactions to be included in the block
        predecessor_hash : Hash
            Hash of the predecessor block to this block
        block_creator_id : String
            ID of the node who created this block
        merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        nonce : Int
            Value for which block hash satisfies criteria of HashCash
        timestamp : Timestamp of the block creation
        consensus_obj : Instance of consensus module
        difficulty: Int
            Difficulty value used for the block mining

        Attributes
        ----------
        _length_in_chain : Int
            Position at which it resides in the node's chain
        _crypto_helper : Instance of the Crypto Helper Module
        _merkle_tree_root : Hash
            Merkle Tree Root of all transactions combined
        _consensus : Instance of consensus module

        """
        super(LogicalBlock, self).__init__(block_id=block_id,
                                           merkle_tree_root=merkle_tree_root,
                                           predecessor_hash=predecessor_hash,
                                           block_creator_id=block_creator_id,
                                           transactions=transactions,
                                           nonce=nonce,
                                           timestamp=timestamp,
                                           difficulty=difficulty)
        self._length_in_chain = None
        self._crypto_helper = CryptoHelper.instance()
        self._consensus = consensus_obj
        if not self._merkle_tree_root:
            self._merkle_tree_root = self.compute_merkle_root()

    def is_block_ours(self, node_id):
        """Checks to see if the block was created by the node ID specified
        in the parameter.

        """
        return self._block_creator_id == node_id

    def get_block_pos(self):
        """Returns position at which block resides in the chain"""
        return self._length_in_chain

    def set_block_pos(self, value):
        """Sets the position at which block will reside in chain"""
        self._length_in_chain = value

    def get_computed_hash(self):
        """Gets the hash for the entire block"""
        return self._crypto_helper.hash(self.to_json_headers())

    @staticmethod
    def from_block(block, consensus_obj):
        """Instantiate LogicalBlock from Block"""
        return LogicalBlock.from_dict(block.to_dict(), consensus_obj)

    @staticmethod
    def from_json(json_data):
        """Deserialize a JSON string to a Block instance."""
        data_dict = json.loads(json_data)
        return LogicalBlock.from_dict(data_dict)

    @staticmethod
    def from_dict(data_dict, consesnus_obj=None):
        """Instantiate a LogicalBlock from a data dictionary."""
        _transactions = []
        if data_dict['transactions']:
            _transactions = data_dict['transactions']
        return LogicalBlock(block_id=data_dict['nr'],
                            merkle_tree_root=data_dict['merkleHash'],
                            predecessor_hash=data_dict['predecessorBlock'],
                            block_creator_id=data_dict['creator'],
                            transactions=[Transaction.from_dict(transaction_dict)
                                          for transaction_dict in _transactions],
                            nonce=data_dict['nonce'],
                            difficulty=data_dict['difficulty'],
                            timestamp=data_dict['timestamp'],
                            consensus_obj=consesnus_obj)

    def get_block_obj(self):
        """Convert LogicalBlock to Block"""
        return Block.from_json(super(LogicalBlock, self).get_json())

    def validate_block(self, _latest_timestamp, _earliest_timestamp,
                       _num_of_blocks, _prev_difficulty, _contracts=None):
        """Validate the block by checking -
           1. The transaction signatures in the block
           2. The Merkle Tree correctness
           3. The Block Hash with given Nonce to see if it
              satisfies the configured number of zeroes.
           4. If the transaction interacts with a contract
              and produces an invalid state

        Returns
        -------
        Integer
            -1 : If Check 1 failed
            -2 : If Check 2 failed
            -3 : If Check 3 failed
            -4 , bad_tx: If Check 4 failed
            0 : If all Checks passed
        """

        # Validate Transaction signatures
        transactions = self._transactions
        if transactions is not None:
            for t in transactions:
                if not t.validate_transaction(self._crypto_helper):
                    self._logger.debug('Invalid transaction: {}'.format(t))
                    return -1

        # Validate Merkle Tree correctness
        if self.compute_merkle_root() != self._merkle_tree_root:
            self._logger.debug('Invalid merkle root: {}'.format(self._merkle_tree_root))
            return -2

        #  validate nonce
        block_valid = self._consensus.validate(self, _latest_timestamp,
                                               _earliest_timestamp,
                                               _num_of_blocks, _prev_difficulty)
        if not block_valid:
            self._logger.debug('Invalid block: {}'.format(self))
            return -3

        bad_tx = self.get_bad_transaction(_contracts)
        if isinstance(bad_tx,Transaction):
            return -4, bad_tx
        
        return 0

    def get_bad_transaction(self, _contracts):
        transactions = self._transactions
        if transactions is not None:
            for t in transactions:
                if t.transaction_type == Transaction_Types().contract_creation:
                    if not self.validate_contract_creation(t):
                        return t
                elif t.transaction_type == Transaction_Types().method_call:
                    try:
                        contract = _contracts[t.receiver]
                    except:
                        return t
                    valid_state = self.validate_method_call(t, contract)
                    if valid_state == None:
                        return t
                    else:
                        _contracts[t.receiver].state = valid_state
                elif t.transaction_type == Transaction_Types().contract_termination:
                    contract = _contracts[t.receiver]
                    if not self.validate_contract_termination(t, contract):
                        return t
                elif t.transaction_type == Transaction_Types().contract_restoration:
                    contract = _contracts[t.receiver]
                    if not self.validate_contract_restoration(t, contract):
                        return t
        return None

    def compute_merkle_root(self):
        """Computes the hashes of all transaction and calls _merkle_root

        Returns
        -------
        Hash
            Merkle Tree root of the transactions
            if no transactions present then return None

        """

        def _merkle_root(hashes):
            """Takes 2 transaction's hashes; concatenate them and
            calculate their hash
            Recursively do this until 1 hash is left

            Parameters
            ----------
            hashes: hashes of transactions

            Returns
            -------
            merkle tree root; final hash of all the hashes
                     or None if param hashes is empty

            """
            sub_tree = []
            for i in range(0, len(hashes), 2):
                # If not the last element
                if i + 1 < len(hashes):
                    # Concatenate the hashes and calculate their hash
                    value = str(hashes[i] + hashes[i + 1]).encode('UTF-8')
                    hash = sha(value).hexdigest()
                else:
                    hash = hashes[i]
                sub_tree.append(hash)
            if len(sub_tree) == 0:
                return None
            elif len(sub_tree) == 1:
                return sub_tree[0]
            else:
                return _merkle_root(sub_tree)

        txn_hashes = []
        if self._transactions is None:
            return None
        for t in self._transactions:
            txn_hashes.append(self._crypto_helper.hash(t.get_json()))
        return _merkle_root(txn_hashes)

    
    def validate_contract_creation(self, tx):
        """Checks if the tx can create a new contract successfully."""
        payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))
        txHash = tx.transaction_hash
        if txHash == None:
            txHash = self._crypto_helper.hash(tx.get_json())

        contract_id = -1
        contract_owners = [tx.sender]
        contract_addresses = [txHash]
        contract_code = payload['contractCode']
        contract = SmartContract(contract_id, contract_owners, contract_addresses, contract_code)

        url = 'http://localhost:' + str(contract.port) + '/createContract'
        try:
            #Add sender at the beginning of the arguments
            arguments = json.dumps(payload['arguments'])
            arguments = arguments.replace('{','{"sender": "' + tx.sender + '", ', 1)
            arguments = json.loads(arguments)

            data = {'sender': tx.sender,
                    'code': payload['contractCode'],
                    'contract_file_name': payload['contract_file_name'],
                    'arguments': arguments
                    }
            r = requests.post(url,json=data).json()
            contract.terminate()
            if(r['success'] == True and r['newState']['bad_state'] == False):
                print('\nContract creation tx was validated.\n')
                return True
            else:
                print('\nContract creation tx was not validated.\n')
                return False
        except:
            logging.error('\nContract creation tx was not validated2.\n')
            return False

    def validate_method_call(self, tx, contract):
        """Checks if a tx can call a method or methods on an existing contract successfully."""
        try:
            url = 'http://localhost:' + str(contract.port) + '/callMethod'

            payload = json.loads(tx.to_dict()['payload'].replace("'",'"'))

            data = {'code': contract.code,
                    'state': contract.state,
                    'contract_file_name': payload['contract_file_name'],
                    'methods': payload['methods'],
                    'sender': tx.sender}
            
            r = requests.post(url,json=data).json()
            if(r['success'] == True 
                and r['encodedUpdatedState'] != contract.state 
                and r['updatedState']['bad_state'] == False):
                    print('\nMethod call was validated.\n')
                    return r['encodedUpdatedState']
            #If the execution wasn't successfull or the tx didn't create any state changes return false
            else:
                print('\nMethod call was not validated.\n')
                return None
        except:
            logging.error('Method call verification could not be completed')
            return None

    def validate_contract_termination(self, tx, contract):
        print("Validating contract termination")
        if (contract != None 
            and contract.terminated == False
            and tx.sender in contract.contract_owners):
            print("Contract termination validated")
            return True
        else:
            print("Contract termination not validated")
            return False


    
    def validate_contract_restoration(self, tx, contract):
        print("Validating contract restoration")
        if (contract != None 
            and contract.terminated == True
            and tx.sender in contract.contract_owners
            and self.validate_contract_creation(tx)):
            print("Contract restoration validated")
            return True
        else:
            print("Contract restoration not validated")
            return False