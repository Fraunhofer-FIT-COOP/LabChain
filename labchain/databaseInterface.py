import json
import logging
import os
import sqlite3

from labchain.datastructure.block import Block
from labchain.datastructure.transaction import Transaction
from labchain.util.TransactionFactory import TransactionFactory


class Db:
    def __init__(self, block_chain_db_file, create_new_database=False):
        """
        Constructor for Database

        Parameters
        ----------
        block_chain_db_file: String
            Location of database file

        Attributes
        ----------
        db_file : Location of database file
        blockchain_table: Name of blockchain table
        transaction_table: Nmae of transaction table
        """
        # Creates or opens a file called mydb with a SQLite3 DB
        self.logger = logging.getLogger(__name__)
        if create_new_database:
            self.logger.debug('Removing database...')
            if os.path.exists(block_chain_db_file):
                os.remove(block_chain_db_file)
                self.logger.debug('Database removed.')
            else:
                self.logger.debug('Database not found.')
        self.db_file = block_chain_db_file
        self.open_connection(block_chain_db_file)
        self.blockchain_table = 'blockchain'
        self.transaction_table = 'transactions'

    def open_connection(self, db_file):
        """Create a database connection to the SQLite database
            specified by db_file

        :param db_file: database file
        :return: Connection object or None
        """
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            self.logger.error(str(e))

    def create_tables(self):
        """Create the tables if they do no exists

        Returns
        -------
        True if table created or already present, false if database error
        """

        create_blockchain_table = "CREATE TABLE IF NOT EXISTS {} " \
            "(hash text PRIMARY KEY, block_id integer NOT NULL, " \
            "merkle_tree_root text, predecessor_hash text NOT NULL, " \
            "block_creator_id text NOT NULL, nonce integer NOT NULL, " \
            "ts timestamp NOT NULL, difficulty integer NOT NULL)".\
            format(self.blockchain_table)

        create_transactions_table = "CREATE TABLE IF NOT EXISTS {}" \
            "(sender text NOT NULL, receiver text NOT NULL, " \
            "payload text NOT NULL, signature text NOT NULL, " \
            "transaction_hash text PRIMARY KEY, block_hash text" \
            " NOT NULL, FOREIGN KEY (block_hash) REFERENCES {}" \
            " (hash))".format(self.transaction_table, self.blockchain_table)
        try:
            self.cursor.execute(create_blockchain_table)
            self.cursor.execute(create_transactions_table)

            self.conn.commit()
            self.conn.close()
        except sqlite3.Error as e:
            self.logger.error("Table creation error: "+ str(e.args[0]))
            return False
        return True

    def save_block(self, block):
        """Saves the block data to blockchain table and its transactions to
        transactions table

        Parameters
        ----------
        block: block object to be saved in database

        Returns
        -------
        True if data saved successfully, False otherwise
        """
        if not block:
            return False
        self.open_connection(self.db_file)
        # save a single block and its correspondent transactions in the db
        block_hash = block.get_computed_hash()
        block_data = [block_hash, block.block_id, block.block_creator_id, block.merkle_tree_root,
                      block.predecessor_hash, block.nonce, block.timestamp, block.difficulty]
        insert_into_blockchain = "INSERT INTO {} (hash, block_id, block_creator_id, " \
             "merkle_tree_root, predecessor_hash, nonce, ts, difficulty) " \
             "VALUES (?,?,?,?,?,?,?,?)".format(self.blockchain_table)
        insert_into_transactions = "INSERT INTO {} (sender, receiver, " \
            "payload, signature, transaction_hash, block_hash) " \
            "VALUES (?,?,?,?,?,?)".format(self.transaction_table)

        try:
            self.cursor.execute(insert_into_blockchain, block_data)
            for t in block.transactions:
                payload = t.payload
                if isinstance(payload, dict):
                    payload = json.dumps(payload)
                self.cursor.execute(insert_into_transactions,
                                    (t.sender, t.receiver, payload, t.signature,
                                     t.transaction_hash, block_hash))
            self.conn.commit()
            self.conn.close()
        except sqlite3.Error as e:
            self.logger.error("Error in adding block: " + str(e.args[0]))
            return False
        return True

    def get_blockchain_from_db(self):
        """Fetch all blocks with their transactions from database

        Returns
        -------
        List of all blocks
        """
        self.open_connection(self.db_file)
        get_block = "SELECT * from {}".format(self.blockchain_table)
        get_transactions = "SELECT * FROM {} WHERE block_hash = ?".format(self.transaction_table)

        self.cursor.execute(get_block)
        blocks = []
        blocks_db = self.cursor.fetchall()
        if len(blocks_db) == 0:
            return None
        for block_db in blocks_db:
            self.cursor.execute(get_transactions, (block_db[0],))
            txns = []
            txns_db = self.cursor.fetchall()
            if len(txns_db) != 0:
                for txn_db in txns_db:
                    try:
                        json_payload = json.loads(txn_db[2])
                        if isinstance(json_payload, dict):
                            transaction_data = {'payload': json_payload, 'signature': txn_db[3], 'sender': txn_db[0],
                                                'receiver': txn_db[1]}
                            txn = TransactionFactory.create_transcation(transaction_data)
                        elif isinstance(json_payload, int):
                            txn = Transaction(txn_db[0], txn_db[1], txn_db[2], txn_db[3])
                        else:
                            txn = None
                    except json.JSONDecodeError:
                        txn = Transaction(txn_db[0], txn_db[1], txn_db[2], txn_db[3])
                    if not txn.transaction_hash:
                        txn.transaction_hash = txn_db[4]
                    txns.append(txn)
            block = Block(block_id=block_db[1], merkle_tree_root=block_db[2],
                          predecessor_hash=block_db[3], block_creator_id=block_db[4],
                          transactions=txns, nonce=block_db[5], timestamp=float(block_db[6]),
                          difficulty=int(block_db[7]))
            blocks.append(block)
        self.conn.close()
        return blocks
