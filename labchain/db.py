import sqlite3


class Db:
    def __init__(self, block_chain_db_file='../database/labchaindb.sqlite'):
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
            conn = sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as e:
            print(e)

        return None

    def create_tables(self):
        # Check if table users does not exist and create it

        text = 'TEXT'
        integer = 'INTEGER'
        create_blockchain_table = 'CREATE TABLE IF NOT EXISTS ' + self.blockchain_table + \
                                  '(block_id integer PRIMARY KEY, merkle_tree_root text NOT NULL, predecessor_' + \
                                  'hash text NOT NULL, block_creator_id text NOT NULL, timestamp text NOT NULL)'

        create_transactions_table = 'CREATE TABLE IF NOT EXISTS ' + self.transaction_table + \
                                    '(sender text NOT NULL, receiver text NOT NULL, payload text NOT NULL, ' + \
                                    'signature text NOT NULL, transaction_hash text PRIMARY KEY, block_id integer ' + \
                                    'NOT NULL, FOREIGN KEY (block_id) REFERENCES ' + self.blockchain_table + \
                                    ' (block_id))'
        try:
            self.cursor.execute(create_blockchain_table)
            self.cursor.execute(create_transactions_table)

            self.conn.commit()
        except sqlite3.Error as e:
            print("Table creation error: ", e.args[0])
            return False
        return True

    def save_whole_block_chain(self, block_list):
        # first iterate the block dictionary and find the block and then save it to the block chain table\
        #  then save the transactions of the block into the transaction table with proper foreign key constraint
        """
        for batch insert follow the code snippet
        users = [(name1,phone1, email1, password1),
         (name2,phone2, email2, password2),
         (name3,phone3, email3, password3)]

        cursor.executemany(''' INSERT INTO users(name, phone, email, password) VALUES(?,?,?,?)''', users)
        db.commit()
        """

    def save_block(self, block):
        # save a single block and its correspondent transactions in the db
        """
        For example follow the code snippet
        cursor.execute('''INSERT INTO users(name, phone, email, password)
                  VALUES(:name,:phone, :email, :password)''',
                  {'name':name1, 'phone':phone1, 'email':email1, 'password':password1})
        """
        block_data = [block.block_id, block.block_creator_id, block.merkle_tree_root, block.predecessor_hash,
                      block.timestamp]
        insert_into_blockchain = 'INSERT INTO ' + self.blockchain_table + '(block_id, block_creator_id, ' + \
                                 'merkle_tree_root, predecessor_hash, timestamp) VALUES (?,?,?,?,?)'
        insert_into_transactions = 'INSERT INTO ' + self.transaction_table + '(sender, receiver, payload, signature' + \
                                   ', transaction_hash, block_id) VALUES (?,?,?,?,?,?)'

        try:
            self.cursor.execute(insert_into_blockchain, block_data)
            for t in block.transactions:
                self.cursor.execute(insert_into_transactions, (t.sender, t.receiver, t.payload, t.signature,
                                    t.transaction_hash, block.block_id))
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error in adding block: ", e.args[0])
            return False
        return True

    def retrieve_block_by_hash(self, block_hash):
        # get the block from db by it's hash
        """

        :param block_hash:
        :return: block
        """
        """
        For example : 
        user_id = 3
        cursor.execute('''SELECT name, email, phone FROM users WHERE id=?''', (user_id,))
        user = cursor.fetchone()
        """
    def retrieve_whole_block_chain_from_db(self):
        """
        :return: blockchain
        """

        """
        For fetching all the block from db follow the code snippet
        cursor.execute('''SELECT name, email, phone FROM users''')
        user1 = cursor.fetchone() #retrieve the first row
        print(user1[0]) #Print the first column retrieved(user's name)
        all_rows = cursor.fetchall()
        for row in all_rows:
    # row[0] returns the first column in the query (name), row[1] returns email column.
            print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))
        """