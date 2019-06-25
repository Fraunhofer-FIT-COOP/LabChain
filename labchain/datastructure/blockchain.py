from datetime import datetime
import json
import logging
import sys

import time

from labchain.datastructure.block import LogicalBlock
from labchain.datastructure.transaction import NoHashError, Transaction_Types, Transaction
from labchain.datastructure.worldState import WorldState

class BlockChain:
    def __init__(self, node_id, tolerance_value, pruning_interval,
                 consensus_obj, txpool_obj, crypto_helper_obj,
                 min_blocks_for_difficulty, db, q):
        self.contract_counter = 1
        self.method_counter = 1
        self.start_time = 0
        """Constructor for BlockChain

        Parameters
        ----------
        node_id : String
            ID of the node running the blockchain
        tolerance_value : Int
            Length required by the longest chain to be switched to
        pruning_interval : Int
            Time given in hours till which the orphan blocks will be stored
        consensus_obj : Instance of consensus module
        txpool_obj : Instance of txpool module
        crypto_helper_obj : Instance of cryptoHelper module
        min_blocks_for_difficulty : Int
            Minimum blocks used to calculate difficulty
        db : Instance of DB to save all blockchain data
        q : Queue to push requests for missing blocks

        Attributes
        ----------
        _node_id : String
            ID of the node running the blockchain
        _blockchain : Dictionary
            Dictionary of blocks in our blockchain
            key = block hash, value = LogicalBlock instance
        _orphan_blocks : Dictionary
            Dictionary of blocks whose predecessor block is not in our chain
            key = predecessor block hash, value = LogicalBlock instance
        _current_branch_heads : List
            List of the block hashes, which are branch heads maintained by the node
        _node_branch_head : Hash value
            Hash value of the branch head this node is following
        _furthest_branching_point : Dictionary
            Information about the point where earliest branching happened in chain
            key = block instance of branching point, value = position in the chain
        _tolerance_level : Int
            Length required by the longest chain to be switched to
        _pruning_interval : Int
            Number of seconds orphan blocks are stored before being deleted
        _consensus : Instance of the consensus module
        _txpool : Instance of the txpool module
        _crypto_helper : Instance of cryptoHelper module
        _db : Instance of database object
        _q = queue to get missing blocks
        _worldState: Instance of WorldState module

        """
        self._logger = logging.getLogger(__name__)
        self._node_id = node_id
        self._blockchain = {}
        self._orphan_blocks = {}
        self._current_branch_heads = []
        self._node_branch_head = None
        self._furthest_branching_point = {"block": None, "position": float("inf")}
        self._tolerance_level = tolerance_value
        self._pruning_interval = pruning_interval * 3600
        self._consensus = consensus_obj
        self._txpool = txpool_obj
        self._crypto_helper = crypto_helper_obj
        self._min_blocks = min_blocks_for_difficulty
        self._active_mine_block = None
        self._db = db
        self._q = q
        self.worldState = WorldState()
        # self._ws_next_block_id_to_check = 0
        # self.worldState_is_updating = False
        # Create the very first Block, add it to Blockchain
        # This should be part of the bootstrap/initial node only
        _first_block = LogicalBlock(block_id=0, timestamp=0)
        _first_block.set_block_pos(0)
        self._first_block_hash = _first_block.get_computed_hash()
        self._blockchain[self._first_block_hash] = _first_block

        self._logger.debug("Added Genesis block --- \n {b} \n".
                     format(b=str(_first_block)))

        self._node_branch_head = self._first_block_hash
        self._current_branch_heads = [self._first_block_hash, ]
        self._logger.debug("BlockChain initialized with genesis block")


    def get_block_range(self, range_start=None, range_end=None):
        """Returns a list of Lblock objects from the blockchain range_start and range_end inclusive.
        Chain followed by this node is the one traversed.
        range_start or range_end are block hashes
        if range_end is not specified, all blocks till end of chain are returned
        if chain couldn't be traversed at some point we have bigger bugs in code
        if range_start or range_end is not found in chain, returns None
        """
        if not range_start:
            range_start = self._first_block_hash
        if not range_end:
            range_end = self._node_branch_head
        _b_hash = range_end

        if any([range_start not in self._blockchain,
                range_end not in self._blockchain]):
            return None

        blocks_range = []
        while _b_hash != range_start:
            _b = self._blockchain.get(_b_hash)
            _b_hash = _b.predecessor_hash
            blocks_range.append(_b)
        if not _b_hash == self._first_block_hash:
            blocks_range.append(self._blockchain.get(_b_hash))
        return blocks_range

    def get_block_by_id(self, block_id):
        """Returns the block if found in blockchain, else returns None"""
        block_list = []
        for _, _block in self._blockchain.items():
            if _block.block_id == block_id:
                block_list.append(_block)
        return block_list

    def get_block_by_hash(self, block_hash):
        """Sends the Block information requested by any neighbour.

        Parameters
        ----------
        block_hash : Hash
            Hash value of the block requested.

        Returns
        -------
        block_info : Json structure
            The Json of Block which was requested
            None if Block was not found in node's chain.

        """

        block_info = None
        _req_block = self._blockchain.get(block_hash, None)
        if _req_block:
            block_info = _req_block.get_json()
        return block_info

    def get_transaction(self, transaction_hash):
        """
        Parameters
        ----------
        transaction_hash: Hash
            Hash of transaction to search for
        Returns
        -------
        Tuple
            (Transaction obj, Block_hash)
        """
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                hash_to_compare = _txn.transaction_hash
                if hash_to_compare is None:
                    hash_to_compare = self._crypto_helper.hash(_txn.get_json())
                if transaction_hash == hash_to_compare:
                    return _txn, _hash
        else:
            return None, None

    def get_contract(self, contract_hash):
        return self.worldState.get_contract(contract_hash)

    def calculate_diff(self, _hash=None):
        """Sends the timestamps of given/latest and nth last block and
        number of blocks between that time

        Parameters
        ----------
        _hash: Hash
            Hash of the block from where to start difficulty calculation

        Returns
        -------
        number_of_blocks: Integer
            Total number of blocks fetched from config or available in chain
        earliest_timestamp: timestamp
            timestamp of the earliest block added
        latest_timestamp: timestamp
            timestamp of the most recent block added
        latest_difficulty: Integer
            difficulty of the latest block
        """
        if not _hash:
            _hash = self._node_branch_head
        last_block_json = self.get_block_by_hash(_hash)
        if last_block_json:
            _last_block = json.loads(last_block_json)
        else:
            return -1, -1, -1, -1

        # if only genesis block present in chain return 0 as timestamps
        # and 1 as difficulty
        if _last_block["nr"] == 0:
            return 0, 0, 1, 1

        avg_difficulty = 0
        # getting timestamp and difficulty of the last block added in the chain
        _latest_timestamp = _last_block['timestamp']
        _latest_difficulty = _last_block['difficulty']
        avg_difficulty += _latest_difficulty

        # setting hash of the second last block
        _hash = _last_block['predecessorBlock']
        # if there is only one block
        _earliest_timestamp = _latest_timestamp
        _number_of_blocks = 1
        # looping over last min_blocks to get the timestamp of the earliest block
        while _number_of_blocks < self._min_blocks:
            _json_block = self.get_block_by_hash(_hash)
            if _json_block is None:
                break
            _block = json.loads(_json_block)
            _id = _block["nr"]
            if _id == 0:
                break
            _earliest_timestamp = _block['timestamp']
            _hash = _block['predecessorBlock']
            avg_difficulty += _block['difficulty']
            _number_of_blocks += 1
        avg_difficulty = float(avg_difficulty) / _number_of_blocks
        return _latest_timestamp, _earliest_timestamp, _number_of_blocks, avg_difficulty

    def add_block(self, block, db_flag=True):
        """Finds correct position and adds the new block to the chain.
        If block predecessor not found in chain, stores block as an orphan.

        Parameters
        ----------
        block : LogicalBlock instance
            The block instance to be added to the chain.
        db_flag : Boolean
            To check if provided block be added to DB or not

        Returns
        -------
        Boolean
            Returns True if block is saved as orphan or in the chain.
            Return False if block validation fails and it is deleted.

        """
        if not isinstance(block, LogicalBlock):
            self._logger.debug("Converting block to logical block ")
            block = LogicalBlock.from_block(block, self._consensus)

        if block.get_computed_hash() in self._blockchain:
            return False

        _prev_hash = block.predecessor_hash
        _curr_block_hash = block.get_computed_hash()
        _curr_block = block

        _latest_ts, _earliest_ts, _num_of_blocks, _latest_difficulty = \
            self.calculate_diff(block.predecessor_hash)

        # Get list of already existing contracts that the transactions in this block
        # interact with.
        transactions = block._transactions
        if transactions is not None:
            _contracts = {}
            for t in transactions:
                if (t.transaction_type == Transaction_Types().method_call
                    or t.transaction_type == Transaction_Types().contract_termination
                    or t.transaction_type == Transaction_Types().contract_restoration):
                    _contracts[t.transaction_hash] = self.worldState.get_contract(t.receiver)
                    
        validity_level = block.validate_block(_latest_ts, _earliest_ts,
                                              _num_of_blocks, _latest_difficulty, _contracts)
        bad_tx = None
        if isinstance(validity_level,tuple):
            bad_tx = validity_level[1]
            validity_level = validity_level[0]


        if _prev_hash not in self._blockchain:
            if validity_level == -3:
                self._logger.debug("Block has been put to orphan pool, "
                                   "since predecessor was not found")
                self._orphan_blocks[_prev_hash] = _curr_block
                self.request_block_from_neighbour(_prev_hash)
        else:
            if not validity_level == 0:
                self._logger.debug("The block received is not valid, "
                                   "discarding this block -- \n {b}".
                                   format(b=str(block)))
                if block.is_block_ours(self._node_id):
                    self._logger.debug("Since this block is ours, returning the "
                                 "transactions back to transaction pool")
                    _txns = block.transactions
                    if isinstance(bad_tx,Transaction):
                        self._txpool.penalize_transaction(bad_tx)
                    self._txpool.return_transactions_to_pool(_txns)
                del block
                return False

            _prev_block = self._blockchain.get(_prev_hash)
            _prev_block_pos = _prev_block.get_block_pos()

            if _prev_hash in self._current_branch_heads:
                self._current_branch_heads.remove(_prev_hash)
            else:
                if _prev_block_pos < self._furthest_branching_point["position"]:
                    self._furthest_branching_point["position"] = _prev_block_pos
                    self._furthest_branching_point["block"] = _prev_block

            _curr_block.set_block_pos(_prev_block_pos + 1)
            self._blockchain[_curr_block_hash] = _curr_block
            self._current_branch_heads.append(_curr_block_hash)
            if db_flag:
                self._db.save_block(block)
                self._logger.info('Saved block no. {} to DB'.format(block.block_id))

            if _prev_hash == self._node_branch_head:
                self._logger.debug("Branch head updated for node {}".format(self._node_id))
                self._node_branch_head = _curr_block_hash

            # Check recursively if blocks are parent to some orphans
            _parent_hash = _curr_block_hash
            _parent_block = _curr_block
            while _parent_hash in self._orphan_blocks:
                _block = self._orphan_blocks[_parent_hash]
                _this_block_hash = _block.get_computed_hash()
                _block.set_block_pos(_parent_block.get_block_pos() + 1)
                self._blockchain[_this_block_hash] = _block
                _parent_hash = _this_block_hash
                _parent_block = _block

        # kill mine check
        if not block.is_block_ours(self._node_id):
            self.check_block_in_mining(block)

        self._logger.info("Added new block --- \n {h} \n {b} \n".
                    format(h=str(block.get_computed_hash()), b=str(block)))

        self._logger.debug("Number of branches currently branch heads = {}"
                           .format(len(self._current_branch_heads)))
        i = 0
        for branch in self._current_branch_heads:
            self._logger.debug("Branch {} : {}".format(i + 1, branch))
            i += 1
        self.switch_to_longest_branch()

        self.update_worldState(block)

        return True

    def create_block(self, transactions):
        """Creates a new LogicalBlock instance.

        Parameters
        ----------
        transactions : List
            Transactions to be associated with the block

        Returns
        -------
        new_block : LogicalBlock instance
            The New Block created from the transactions given

        """

        _curr_head = self._blockchain[self._node_branch_head]
        _new_block_id = _curr_head.block_id + 1
        new_block = LogicalBlock(block_id=_new_block_id,
                                 transactions=transactions,
                                 predecessor_hash=self._node_branch_head,
                                 block_creator_id=self._node_id,
                                 consensus_obj=self._consensus)
        return new_block

    def switch_to_longest_branch(self):
        """Functionality to switch to the longest chain among all the
        chains currently maintained by blockchain.
        Switches only if the length of one of the chains is more than
        the tolerance level defined.

        """
        if len(self._current_branch_heads) == 1:
            # No Branching happened yet, nothing to do here
            return

        _check_point_pos = self._furthest_branching_point['position']
        _check_point = self._furthest_branching_point['block']
        _check_point_hash = _check_point.get_computed_hash()

        _max_len = 0
        _max_head = None
        for _branch_head_hash in self._current_branch_heads:
            _head = self._blockchain.get(_branch_head_hash)
            _path_len = _head.get_block_pos() - _check_point_pos
            if _path_len > _max_len:
                _max_len = _path_len
                _max_head = _head

        if _max_len > self._tolerance_level:
            self._logger.debug("Crossed Tolerance level, branch switching took place")
            _new_head_hash = _max_head.get_computed_hash()

            # Save all block hashes between furthest branch and head in max chain
            _b_hash = _new_head_hash
            _longest_chain = []
            while _b_hash != _check_point_hash:
                _longest_chain.append(_b_hash)
                _b = self._blockchain.get(_b_hash)
                _b_hash = _b.predecessor_hash
            _longest_chain.append(_check_point_hash)

            # Remove all other branches
            # self._current_branch_heads.remove(_new_head_hash)
            for _head in self._current_branch_heads:
                _b_hash = _head
                while _b_hash not in _longest_chain:
                    _b = self._blockchain.pop(_b_hash)
                    if _b.is_block_ours(self._node_id):
                        _txns = _b.transactions
                        self._txpool.return_transactions_to_pool(_txns)
                    _b_hash = _b.predecessor_hash
                    del _b

            self._current_branch_heads = [_new_head_hash, ]
            self._node_branch_head = _new_head_hash
            self._furthest_branching_point = {"block": None, "position": float("inf")}
            self._logger.debug("Branch switching successful, new node branch head : {}".
                         format(self._node_branch_head))
            
            # Update contract states to the new branch
            self.worldState.remove_contract_states(_check_point.block_id)
            for block in self._blockchain.values():
                if block.block_id > _check_point.block_id:
                    self.update_worldState(block)

    def prune_orphans(self):
        """Delete orphans stored in the orphan store once the pruning
        interval as defined in config has crossed
        """
        _curr_time = datetime.now()
        for _hash in self._orphan_blocks:
            _block = self._orphan_blocks[_hash]
            _block_creation_time = datetime.fromtimestamp(_block.timestamp)
            _time_passed = (_curr_time - _block_creation_time).total_seconds()
            if _time_passed >= self._pruning_interval:
                self._orphan_blocks.pop(_hash)
                del _block


    def update_worldState(self, block):
        for tx in block.transactions:
            txType = tx.transaction_type
            txHash = tx.transaction_hash
            if txHash == None:
                txHash = self._crypto_helper.hash(tx.get_json().encode())

            txTypes_instance = Transaction_Types()
            if(txType == txTypes_instance.normal_transaction):
                print("\nNormal tx detected in Block #" + str(block.block_id) + " with tx.hash " + txHash)
                continue
            if (txType == txTypes_instance.contract_creation):
                # print("\nContract creation tx detected in Block #" + 
                #     str(block.block_id) + " with tx.hash " + str(txHash))
                
                if self.contract_counter == 1:
                    self.start_time = time.time()
                elapsed_time = time.time() - self.start_time
                print('Contract creation # ' + str(self.contract_counter) + '. Elapsed time: ' + str(elapsed_time))

                #print('Contract # ' + str(self.contract_counter))
                self.contract_counter = self.contract_counter + 1
                self.worldState.create_contract(tx, block.block_id)
                print('Contract created\n')
            if (txType == txTypes_instance.method_call):
                # print("\nmethod call tx detected in Block #" + 
                #     str(block.block_id) + " with tx.hash " + txHash)
                if self.method_counter == 1:
                    self.start_time = time.time()
                elapsed_time = time.time() - self.start_time
                print('Method call # ' + str(self.method_counter) + '. Elapsed time: ' + str(elapsed_time))
                self.method_counter = self.method_counter + 1
                self.worldState.call_method(tx, block.block_id)
                print('Method called on contract')
            if (txType == txTypes_instance.contract_termination):
                print("\nContract Termination tx detected in Block #" + 
                    str(block.block_id) + " with tx.hash " + txHash)
                self.worldState.terminate_contract(tx.receiver, tx.sender)
                print('Contract Terminated')
            if (txType == txTypes_instance.contract_restoration):
                print("\nContract Restoration tx detected in Block #" + 
                    str(block.block_id) + " with tx.hash " + txHash)
                self.worldState.restore_contract(tx, block.block_id)
                print('Contract Restored\n')


    def request_block_from_neighbour(self, requested_block_hash):
        """Requests a block from other nodes connected with.

        Parameters
        ----------
        add hash to request queue

        """
        self._q.put(requested_block_hash)

    def active_mine_block_update(self, block):
        """Update the info for the block being mined"""
        self._active_mine_block = block

    def check_block_in_mining(self, block):
        """Check the block received in parameter with the one being mined,
        and kill if the blocks are same with respect to miningself.
        Returns the transactions in the block, after the block is destroyed

        """
        self._logger.info("Kill mine check")
        if self._active_mine_block is not None:
            if block.mine_equality(self._active_mine_block):
                self._logger.info("Kill mine equality true")
                self._consensus.kill_mine = 1
                try:
                    unmined_transactions = list(
                        set(self._active_mine_block.transactions).difference(set(block.transactions)))
                except (TypeError, NoHashError):
                    for t in self._active_mine_block.transactions:
                        if not t.transaction_hash:
                            thash = self._crypto_helper.hash(t.get_json())
                            t.transaction_hash = thash
                    for t in block.transactions:
                        if not t.transaction_hash:
                            thash = self._crypto_helper.hash(t.get_json())
                            t.transaction_hash = thash
                    unmined_transactions = list(
                        set(self._active_mine_block.transactions).difference(set(block.transactions)))
                self._txpool.return_transactions_to_pool(unmined_transactions)
