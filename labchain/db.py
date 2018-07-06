import sqlite3
from labchain.block import Block
from labchain.transaction import Transaction


class Db:
    def __init__(self, block_chain_db_file):
        # Creates or opens a file called mydb with a SQLite3 DB
        self.conn = self.create_connection(block_chain_db_file)
        self.cursor = self.conn.cursor()
        self.blockchain_table = 'blockchain'
        self.transaction_table = 'transactions'

    @staticmethod
    def create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None

    def create_tables(self):
        # Check if table users does not exist and create it

        create_blockchain_table = 'CREATE TABLE IF NOT EXISTS ' + self.blockchain_table + \
                                  '(hash text PRIMARY KEY, block_id integer NOT NULL, merkle_tree_root text, ' + \
                                  'predecessor_hash text NOT NULL, block_creator_id text NOT NULL, nonce integer ' + \
                                  'NOT NULL, timestamp timestamp NOT NULL, difficulty integer NOT NULL)'

        create_transactions_table = 'CREATE TABLE IF NOT EXISTS ' + self.transaction_table + \
                                    '(sender text NOT NULL, receiver text NOT NULL, payload text NOT NULL, ' + \
                                    'signature text NOT NULL, transaction_hash text PRIMARY KEY, block_hash text' + \
                                    ' NOT NULL, FOREIGN KEY (block_hash) REFERENCES ' + self.blockchain_table + \
                                    ' (hash))'
        try:
            self.cursor.execute(create_blockchain_table)
            self.cursor.execute(create_transactions_table)

            self.conn.commit()
        except sqlite3.Error as e:
            print("Table creation error: ", e.args[0])
            print(e)
            return False
        return True

    def save_block(self, block):
        # save a single block and its correspondent transactions in the db
        """
        For example follow the code snippet
        cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(:name,:phone, :email, :password)''',
                  {'name':name1, 'phone':phone1, 'email':email1, 'password':password1})
        """
        block_hash = block.get_computed_hash()
        block_data = [block_hash, block.block_id, block.block_creator_id, block.merkle_tree_root,
                      block.predecessor_hash, block.nonce, block.timestamp, block.difficulty]
        insert_into_blockchain = 'INSERT INTO ' + self.blockchain_table + '(hash, block_id, block_creator_id, ' + \
                                 'merkle_tree_root, predecessor_hash, nonce, timestamp, difficulty) VALUES (?,?,?,?,?,?,?,?)'
        insert_into_transactions = 'INSERT INTO ' + self.transaction_table + '(sender, receiver, payload, signature' + \
                                   ', transaction_hash, block_hash) VALUES (?,?,?,?,?,?)'

        try:
            self.cursor.execute(insert_into_blockchain, block_data)
            for t in block.transactions:
                self.cursor.execute(insert_into_transactions, (t.sender, t.receiver, t.payload, t.signature,
                                    t.transaction_hash, block_hash))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error in adding block: ", e.args[0])
            return False
        return True

    def get_blockchain_from_db(self):
        get_block = 'SELECT * from '+self.blockchain_table
        get_transactions = 'SELECT * FROM ' + self.transaction_table + ' WHERE block_hash = ?'

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
                    txn = Transaction(txn_db[0], txn_db[1], txn_db[2], txn_db[3])
                    txn.transaction_hash = txn_db[4]
                    txns.append(txn)
            block = Block(block_db[1], txns, block_db[3], block_db[4], block_db[2], block_db[5], float(block_db[6]), int(block_db[7]))
            blocks.append(block)
        return blocks
