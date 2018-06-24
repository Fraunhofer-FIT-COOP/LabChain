import sqlite3
from sqlite3 import Error
from labchain.singleton import Singleton
import logging

logger = logging.getLogger(__name__)


@Singleton
class DashBoardDB:

    def __init__(self):
        self.path = 'dashboard.db'
        self.conn = None
        self.already_created = True
        self.sql_create_blocks_table = """ CREATE TABLE IF NOT EXISTS blocks(
                                                id integer PRIMARY KEY,
                                                numOfTransactions integer NOT NULL,
                                                creator text NOT NULL
                                            ); """
        self.sql_create_transactions_table = """ CREATE TABLE IF NOT EXISTS transactions(
                                                id integer PRIMARY KEY AUTOINCREMENT,
                                                sender text NOT NULL,
                                                receiver text NOT NULL,
                                                payload text NOT NULL,
                                                block_id integer,
                                                FOREIGN KEY(block_id) REFERENCES blocks(id)
                                            ); """
        self.sql_create_block_chain_status_table = """ CREATE TABLE IF NOT EXISTS blockChainStatus(
                                                id integer PRIMARY KEY AUTOINCREMENT,
                                                blockChainLength integer NOT NULL,
                                                numberOfTransactions integer NOT NULL,
                                                currentDifficulty integer NOT NULL,
                                                nodesConnected integer NOT NULL,
                                                minMiningTime integer NOT NULL,
                                                maxMiningTime integer NOT NULL,
                                                averageMiningTime integer NOT NULL,
                                                miningStatus integer NOT NULL
                                            ); """
        self.create_connection()
        self.initial_checks()
        self.close_connection()

    def create_connection(self):

        try:
            self.conn = sqlite3.connect(self.path)
        except Error as e:
            print(e)

    def initial_checks(self):
        if self.already_created:
            self.create_tables()
            self.conn.commit()
            self.already_created = False
            if self.get_mining_status_init() is None:
                self.initialise_block_chain_status()

    def close_connection(self):
        self.conn.commit()
        self.conn.close()

    def create_tables(self):
        self.create_table(self.sql_create_blocks_table)
        self.create_table(self.sql_create_transactions_table)
        self.create_table(self.sql_create_block_chain_status_table)

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def initialise_block_chain_status(self):
        values = (0, 0, 1, 1, '', '', '', 1)
        self.conn.cursor().execute("insert into blockChainStatus(blockChainLength,numberOfTransactions,"
                                   "currentDifficulty,nodesConnected,minMiningTime,maxMiningTime"
                                   ",averageMiningTime,miningStatus) values (?,?,?,?,?,?,?,?)", values)

    def add_block(self, block):
        self.create_connection()
        block_values = (block.block_id, len(block.transactions), block.block_creator_id[-4:])
        self.conn.cursor().execute("insert into blocks(id,numOfTransactions,creator) values (?,?,?)", block_values)
        for i in range(0, len(block.transactions)):
            trans_values = (block.transactions[i].to_dict()['sender'], block.transactions[i].to_dict()['receiver'],
                            block.transactions[i].to_dict()['payload'], block.block_id)
            self.conn.cursor().execute("insert into transactions(sender,receiver,payload,block_id) values (?,?,?,?)",
                                       trans_values)
        self.close_connection()
        logger.debug('#INFO:DashBoardDB-> Block: ' + str(block.block_id) + 'added to the db.')

    def change_block_chain_length(self, new_length):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET blockChainLength = ? WHERE id = 1;", (new_length,))
        self.close_connection()

    def change_num_of_transactions(self, num_of_transactions):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET numberOfTransactions = ? WHERE id = 1;",
                                   (num_of_transactions,))
        self.close_connection()

    def change_current_diff(self, curr_diff):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET currentDifficulty = ? WHERE id = 1;",
                                   (curr_diff,))
        self.close_connection()

    def change_num_of_nodes(self, num_of_nodes):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET nodesConnected = ? WHERE id = 1;",
                                   (num_of_nodes,))
        self.close_connection()

    def change_min_mining_time(self, min_mining_time):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET minMiningTime = ? WHERE id = 1;",
                                   (min_mining_time,))
        self.close_connection()

    def change_max_mining_time(self, max_mining_time):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET maxMiningTime = ? WHERE id = 1;",
                                   (max_mining_time,))
        self.close_connection()

    def change_avg_mining_time(self, avg_mining_time):
        self.create_connection()
        self.conn.cursor().execute("UPDATE blockChainStatus SET averageMiningTime = ? WHERE id = 1;",
                                   (avg_mining_time,))
        self.close_connection()

    def get_mining_status_init(self):
        cur = self.conn.cursor()
        cur.execute("SELECT miningStatus FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        return result

    def get_mining_status(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT miningStatus FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_num_of_nodes(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT nodesConnected FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_current_diff(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT currentDifficulty FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_num_of_transactions(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT numberOfTransactions FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_block_chain_length(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT blockChainLength FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_min_mining_time(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT minMiningTime FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_max_mining_time(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT maxMiningTime FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result

    def get_avg_mining_time(self):
        self.create_connection()
        cur = self.conn.cursor()
        cur.execute("SELECT averageMiningTime FROM blockChainStatus  WHERE id = 1;")
        result = cur.fetchone()
        if result is not None:
            result = result[0]
        self.close_connection()
        return result
