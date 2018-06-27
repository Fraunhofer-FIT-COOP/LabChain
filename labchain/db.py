import sqlite3


class Db:
    def __init__(self, block_chain_db_file):
        # Creates or opens a file called mydb with a SQLite3 DB
        self.db = sqlite3.connect(block_chain_db_file)
        self.cursor = self.db.cursor()

    def create_tables(self):
        # Get a cursor object
        # Check if table users does not exist and create it
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
                                  blockchain(Id INTEGER PRIMARY KEY, timestamp TEXT, merkle_tree_root TEXT, predecessor_hash TEXT unique, block_creator_id TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS
                                      transaction(Id INTEGER PRIMARY KEY, sender TEXT, receiver TEXT, payload TEXT,blockId integer, foreign key(blockId) references blockchain(Id))''')

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