import json
import logging
import threading
from datetime import datetime

from labchain.datastructure.block import LogicalBlock
from labchain.datastructure.taskTransaction import TaskTransaction
from labchain.datastructure.taskTransaction import WorkflowTransaction
from labchain.datastructure.transaction import NoHashError


class BlockChain:
    def __init__(self, node_id, tolerance_value, pruning_interval,
                 consensus_obj, txpool_obj, crypto_helper_obj,
                 min_blocks_for_difficulty, db, q):
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

        """
        self._logger = logging.getLogger(__name__)
        self._node_id = node_id
        self._blockchain = {}
        self._orphan_blocks = {}
        self._current_branch_heads = []
        self._node_branch_head = None
        self._furthest_branching_point = {"block": None,
                                          "position": float("inf")}
        self._tolerance_level = tolerance_value
        self._pruning_interval = pruning_interval * 3600
        self._consensus = consensus_obj
        self._txpool = txpool_obj
        self._crypto_helper = crypto_helper_obj
        self._min_blocks = min_blocks_for_difficulty
        self._active_mine_block = None
        self._db = db
        self._q = q

        # RLock allows for recursive use of add_block
        self._blockchain_lock = threading.RLock()
        self._orphan_lock = threading.RLock()

        # Create the very first Block, add it to Blockchain
        # This should be part of the bootstrap/initial node only
        _first_block = LogicalBlock(block_id=0, timestamp=0)
        _first_block.set_block_pos(0)
        self._first_block_hash = _first_block.get_computed_hash()
        self._blockchain[self._first_block_hash] = _first_block

        self._logger.debug("Added Genesis block --- \n {b} \n"
                           .format(b=str(_first_block)))

        self._node_branch_head = self._first_block_hash
        self._current_branch_heads = [self._first_block_hash, ]
        self._logger.debug("BlockChain initialized with genesis block")

    def get_block_range(self, range_start=None, range_end=None):
        """Returns a list of Logicalblock objects from the blockchain range_start and range_end inclusive.
        Chain followed by this node is the one traversed.
        range_start or range_end are block hashes
        if range_end is not specified, all blocks till end of chain are returned
        if chain couldn't be traversed at some point we have bigger bugs in code
        if range_start or range_end is not found in chain, returns None
        """
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("get_block_by_range was unable to acquire lock")
            raise TimeoutError

        if not range_start:
            range_start = self._first_block_hash
        if not range_end:
            range_end = self._node_branch_head
        _b_hash = range_end

        if any([range_start not in self._blockchain,
                range_end not in self._blockchain]):
            self._blockchain_lock.release()
            return None

        blocks_range = []
        while _b_hash != range_start:
            _b = self._blockchain.get(_b_hash)
            _b_hash = _b.predecessor_hash
            blocks_range.append(_b)
        if not _b_hash == self._first_block_hash:
            blocks_range.append(self._blockchain.get(_b_hash))
        self._blockchain_lock.release()
        return blocks_range

    def get_block_by_id(self, block_id):
        """Returns the block if found in blockchain, else returns None"""
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("get_block_by_id was unable to acquire lock")
            raise TimeoutError

        block_list = []
        for _, _block in self._blockchain.items():
            if _block.block_id == block_id:
                block_list.append(_block)
        self._blockchain_lock.release()
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
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("get_block_by_hash was unable to acquire lock")
            raise TimeoutError

        block_info = None
        _req_block = self._blockchain.get(block_hash, None)
        if _req_block:
            block_info = _req_block.get_json()
        self._blockchain_lock.release()
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
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("get_transaction was unable to acquire lock")
            raise TimeoutError

        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                if transaction_hash == _txn.transaction_hash:
                    self._blockchain_lock.release()
                    return _txn, _hash
        pool_transaction = self._txpool.get_transaction_by_hash(transaction_hash)[0]
        if pool_transaction:
            self._blockchain_lock.release()
            return pool_transaction, "No block hash - this transaction still in the pool"
        else:
            self._blockchain_lock.release()
            return None, None

    def get_all_transactions(self):
        """
        Returns
        -------
        Tuple
            (Transaction obj, Block_hash)
        """
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "get_all_transactions was unable to acquire lock")
            raise TimeoutError

        res = []
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                res.append(_txn)
        self._blockchain_lock.release()
        return res

    def search_transaction_from_receiver(self, receiver_public_key):
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "search_transaction_from_receiver was unable to acquire lock")
            raise TimeoutError

        res = []
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                if _txn.receiver == receiver_public_key:
                    res.append(_txn)
        self._blockchain_lock.release()
        return res

    def search_transaction_from_sender(self, sender_public_key):
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "search_transaction_from_sender was unable to acquire lock")
            raise TimeoutError

        res = []
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                if _txn.sender == sender_public_key:
                    res.append(_txn)
        self._blockchain_lock.release()
        return res

    def get_task_transactions(self):
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "get_task_transactions was unable to acquire lock")
            raise TimeoutError

        task_transactions = []
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                if isinstance(_txn, TaskTransaction) and not isinstance(_txn, WorkflowTransaction):
                    task_transactions.append(_txn)
        self._blockchain_lock.release()
        return task_transactions

    def get_workflow_transactions(self):
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "get_workflow_transaction was unable to acquire lock")
            raise TimeoutError

        task_transactions = []
        for _hash, _block in self._blockchain.items():
            _txns = _block.transactions
            for _txn in _txns:
                if isinstance(_txn, WorkflowTransaction):
                    task_transactions.append(_txn)
        self._blockchain_lock.release()
        return task_transactions

    def get_n_last_transactions(self, n):
        """
        Parameters
        ----------
        n: numbers of last mined transactions
        Returns
        -------
        array of transactions
        """
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "get_n_last_transactions was unable to acquire lock")
            raise TimeoutError

        n = int(n)
        number_of_transactions = 0
        total_transactions = []
        current_block_hash = self._node_branch_head
        while (number_of_transactions < n
               and self._blockchain[current_block_hash].block_id != 0):
            remained_transactions = n - number_of_transactions
            block_transactions = self._blockchain[current_block_hash].transactions[:remained_transactions]
            current_block_hash = self._blockchain[current_block_hash].predecessor_hash
            total_transactions.extend(block_transactions)
            number_of_transactions += len(block_transactions)
        self._blockchain_lock.release()
        return total_transactions

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
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("calculate_diff was unable to acquire lock")
            raise TimeoutError

        if not _hash:
            _hash = self._node_branch_head
        last_block_json = self.get_block_by_hash(_hash)
        if last_block_json:
            _last_block = json.loads(last_block_json)
        else:
            self._blockchain_lock.release()
            return -1, -1, -1, -1

        # if only genesis block present in chain return 0 as timestamps
        # and 1 as difficulty
        if _last_block["nr"] == 0:
            self._blockchain_lock.release()
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
        self._blockchain_lock.release()
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
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("Add block was unable to acquire lock")
            raise TimeoutError

        # Convert block to LogicalBlock if necessary
        if not isinstance(block, LogicalBlock):
            self._logger.debug("Converting block to logical block!")
            block = LogicalBlock.from_block(block, self._consensus)

        if block.get_computed_hash() in self._blockchain:
            self._logger.debug("Hash already present in blockchain! Not adding.")
            self._blockchain_lock.release()
            return False

        validation_result = self._get_validation_data(block)

        if validation_result == 0:  # Block is valid and can be added
            self._add_block_to_blockchain(block, db_flag)
            self._check_for_orphans_with_parent(db_flag)  # New block might be predecessor of orphans
        elif validation_result == -1:  # Block is invalid and has to be discarded
            self._logger.debug("The block received is not valid, discarding this block -- \n {b}".format(b=str(block)))
            if block.is_block_ours(self._node_id):
                self._logger.debug("Since this block is ours, returning the transactions back to transaction pool")
                _txns = block.transactions
                self._txpool.return_transactions_to_pool(_txns)
            del block
            self._logger.debug("Block not valid! Not adding.")
            self._blockchain_lock.release()
            return False
        elif validation_result == -2:  # Blocks seems to be an orphan and is added to orphan_pool
            self._add_block_to_orphan_pool(block)
        else:  # This case could be relevant in future and informs about possible bugs
            self._logger.error('Unexpected block state')
            self._blockchain_lock.release()
            raise ValueError

        # kill mine check
        if not block.is_block_ours(self._node_id):
            self.check_block_in_mining(block)

        self._logger.info("Added new block --- \n {h} \n {b} \n"
                          .format(h=str(block.get_computed_hash()),
                                  b=str(block)))
        self._logger.debug("Number of branches currently branch heads = {}"
                           .format(len(self._current_branch_heads)))
        i = 0
        for branch in self._current_branch_heads:
            self._logger.debug("Branch {} : {}".format(i + 1, branch))
            i += 1

        self._blockchain_lock.release()

        self.switch_to_longest_branch()
        return True

    def _get_validation_data(self, block: LogicalBlock):
        """
        Evaluates block for addition to blockchain
        :param block: block to be checked
        :return:
             0 - block is valid
            -1 - block is invalid and not orphan, discard
            -2 - block is orphan, might be valid in future
        """
        _prev_hash = block.predecessor_hash
        _curr_block_hash = block.get_computed_hash()
        _curr_block = block

        _latest_ts, _earliest_ts, _num_of_blocks, _latest_difficulty = self.calculate_diff(block.predecessor_hash)
        validity_level = block.validate_block(_latest_ts, _earliest_ts, _num_of_blocks, _latest_difficulty)

        if validity_level == -1:
            return -1  # discard invalid blocks
        elif validity_level == -2:
            return -1  # discard invalid blocks
        elif validity_level == -3 and _prev_hash in self._blockchain:
            return -1  # discard invalid block
        elif validity_level == -3 and _prev_hash not in self._blockchain:
            return -2  # block might be orphan
        else:
            return 0

    def _add_block_to_blockchain(self, block: LogicalBlock, db_flag):
        """
        A valid block is added to the blockchain
        :param block:   the block to be added to the blockchain
        :param db_flag: True, if block should be added to database
        """
        _prev_block = self._blockchain.get(block.predecessor_hash)
        _prev_block_pos = _prev_block.get_block_pos()

        if block.predecessor_hash in self._current_branch_heads:
            self._current_branch_heads.remove(block.predecessor_hash)
        else:
            if _prev_block_pos < self._furthest_branching_point["position"]:
                self._furthest_branching_point["position"] = _prev_block_pos
                self._furthest_branching_point["block"] = _prev_block

        block.set_block_pos(_prev_block_pos + 1)
        self._blockchain[block.get_computed_hash()] = block
        self._current_branch_heads.append(block.get_computed_hash())
        if db_flag:
            self._db.save_block(block)
            self._logger.info('Saved block no. {} to DB'.format(block.block_id))

        if block.predecessor_hash == self._node_branch_head:
            self._logger.debug("Branch head updated for node {}".format(self._node_id))
            self._node_branch_head = block.get_computed_hash()

    def _add_block_to_orphan_pool(self, block: LogicalBlock):
        """
        A orphan is added to the orphan_pool
        :param block: the block to be added to the orphan_pool
        :raises TimeoutError if orphan_pool cannot be accessed
        """
        self._logger.debug("Block has been put to orphan pool, since predecessor was not found")
        # Protection mechanism for multithreading
        if not self._orphan_lock.acquire(timeout=5):
            self._logger.debug("Add block was unable to acquire orphan_lock")
            raise TimeoutError
        """
        The case that multiple orphans could have the same predecessor block was not considered in the previous
        version of the code. In this refactoring, the logic to add orphans to the blockchain if predecessors arrive
        has been added. Idea to implement this would be to modify the dictionary so that a list of orphans is saved
        for each predecessor-hash
        """
        if block.predecessor_hash in self._orphan_blocks:
            self._logger.warning("Orphan with same predecessor already in orphan_pool, overwriting")  # TODO fix logic
        self._orphan_blocks[block.predecessor_hash] = block
        self._orphan_lock.release()
        self.request_block_from_neighbour(block.predecessor_hash)

    def _check_for_orphans_with_parent(self, db_flag):
        """
        Checks, if adding orphans to the blockchain results in other orphans finding their predecessor. If so, these
        blocks should be added too.
        :param db_flag: flag passed to _add_block_to_blockchain (due to recursive calls)
        :raises TimeoutError if orphan_pool cannot be accessed
        :raises ValueError if orphan is still considered in orphan although predecessor is in blockchain
        """
        # Protection mechanism for multithreading
        if not self._orphan_lock.acquire(timeout=5):
            self._logger.debug(
                "Add block was unable to acquire orphan_lock")
            raise TimeoutError

        predecessor_is_in_blockchain = self._get_orphans_with_predecessor_in_blockchain()

        # Add blocks with predecessor in blockchain to blockchain
        for predecessor_hash in predecessor_is_in_blockchain:  # Checks each block in orphan_pool
            block = predecessor_is_in_blockchain[predecessor_hash]
            validation_result = self._get_validation_data(block)  # Revalidation of block
            if validation_result == 0:  # former orphan is now a valid block and is added
                self._add_block_to_blockchain(block, db_flag)
            elif validation_result == -1:  # former orphan is invalid and should be discarded
                self._logger.debug("The block taken from orphan_pool is not valid, discarding this block -- \n {b}"
                                   .format(b=str(block)))
                if block.is_block_ours(self._node_id):
                    self._logger.debug("Since this block is ours, returning the transactions back to transaction pool")
                    _txns = block.transactions
                    self._txpool.return_transactions_to_pool(_txns)
                del block
                self._logger.debug("Block not valid! Not adding.")
            else:
                """
                    validation_result -2 cannot happen, because block was taken from orphan pool and cannot be an 
                    orphan again since predecessor is now in blockchain
                """
                self._logger.error('Unexpected block state')
                self._orphan_lock.release()
                raise ValueError

        # Remove non-orphans from orphan_pool
        self._orphan_blocks = {k: predecessor_is_in_blockchain[k] for k in
                               set(predecessor_is_in_blockchain) - set(self._orphan_blocks)}
        if len(
                predecessor_is_in_blockchain) == 0:  # All orphans have predecessors not in blockchain, terminate recursion
            self._orphan_lock.release()
            return
        else:  # Check if orphans got a parent in blockchain
            self._check_for_orphans_with_parent(db_flag)
            self._orphan_lock.release()

    def _get_orphans_with_predecessor_in_blockchain(self):
        """
        Searches for orphans where a predecessor can be found
        :return: list of orphans with predecessor
        """
        _pred_is_in_blockchain = {}
        for _orphan_predecessor_hash in self._orphan_blocks:
            if _orphan_predecessor_hash in self._blockchain:
                _pred_is_in_blockchain[_orphan_predecessor_hash] = self._orphan_blocks[_orphan_predecessor_hash]
        return _pred_is_in_blockchain

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
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug("create_block was unable to acquire lock")
            raise TimeoutError

        _curr_head = self._blockchain[self._node_branch_head]
        _new_block_id = _curr_head.block_id + 1
        new_block = LogicalBlock(block_id=_new_block_id,
                                 transactions=transactions,
                                 predecessor_hash=self._node_branch_head,
                                 block_creator_id=self._node_id,
                                 consensus_obj=self._consensus)
        self._blockchain_lock.release()
        return new_block

    def switch_to_longest_branch(self):
        """Functionality to switch to the longest chain among all the
        chains currently maintained by blockchain.
        Switches only if the length of one of the chains is more than
        the tolerance level defined.

        """
        # Protection mechanism for multithreading
        if not self._blockchain_lock.acquire(timeout=5):
            self._logger.debug(
                "Switch_to_longest_branch was unable to acquire lock")
            raise TimeoutError

        if len(self._current_branch_heads) == 1:
            # No Branching happened yet, nothing to do here
            self._blockchain_lock.release()
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
            self._furthest_branching_point = {"block": None,
                                              "position": float("inf")}
            self._logger.debug(
                "Branch switching successful, new node branch head : {}"
                .format(self._node_branch_head))
            self._blockchain_lock.release()

    def prune_orphans(self):
        """Delete orphans stored in the orphan store once the pruning
        interval as defined in config has crossed
        """
        # Protection mechanism for multithreading
        if not self._orphan_lock.acquire(timeout=5):
            self._logger.debug("get_block_by_hash was unable to acquire lock")
            raise TimeoutError

        _curr_time = datetime.now()
        for _hash in self._orphan_blocks:
            _block = self._orphan_blocks[_hash]
            _block_creation_time = datetime.fromtimestamp(_block.timestamp)
            _time_passed = (_curr_time - _block_creation_time).total_seconds()
            if _time_passed >= self._pruning_interval:
                self._orphan_blocks.pop(_hash)
                del _block
        self._orphan_lock.release()

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
