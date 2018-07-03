from labchain.singleton import Singleton
import logging
import paho.mqtt.publish as publish
import os.path

logger = logging.getLogger(__name__)


@Singleton
class DashBoardDB:

    def __init__(self):
        self.path = 'dashboard.db'
        self.conn = None
        self.already_created = True
        self.block_chain_length = 0
        self.num_of_blocks = 0
        self.num_of_transactions = 0
        self.curr_diff = 0
        self.num_of_nodes = 0
        self.min_mining_time = 0
        self.max_mining_time = 0
        self.avg_mining_time = 0
        self.mining_status = 0
        self.block_chain_memory_size = 0
        self.plot_dir = ''
        self.block_file_location = ''

    def set_plot_dir(self, plot_dir):
        self.plot_dir = plot_dir

    def change_block_chain_length(self, new_length):
        self.block_chain_length = new_length

    def change_mining_status(self, mining_status):
        self.mining_status = mining_status

    def change_num_of_blocks(self, num_of_blocks):
        self.num_of_blocks = num_of_blocks

    def change_num_of_transactions(self, num_of_transactions):
        self.num_of_transactions = num_of_transactions

    def change_current_diff(self, curr_diff):
        self.curr_diff = curr_diff

    def change_num_of_nodes(self, num_of_nodes):
        self.num_of_nodes = num_of_nodes

    def change_min_mining_time(self, min_mining_time):
        self.min_mining_time = min_mining_time

    def change_max_mining_time(self, max_mining_time):
        self.max_mining_time = max_mining_time

    def change_avg_mining_time(self, avg_mining_time):
        self.avg_mining_time = avg_mining_time

    def change_block_chain_memory_size(self, memory_size):
        self.block_chain_memory_size += memory_size

    def get_mining_status(self):
        return self.mining_status

    def get_num_of_nodes(self):
        return self.num_of_nodes

    def get_current_diff(self):
        return self.curr_diff

    def get_num_of_transactions(self):
        return self.num_of_transactions

    def get_block_chain_length(self):
        return self.block_chain_length

    def get_num_of_blocks(self):
        return self.num_of_blocks

    def get_min_mining_time(self):
        return self.min_mining_time

    def get_max_mining_time(self):
        return self.max_mining_time

    def get_avg_mining_time(self):
        return self.avg_mining_time

    def get_block_chain_memory_size(self):
        return self.block_chain_memory_size

    def get_block_by_hash_redirect(self, block_hash):
        if os.path.isfile(str(self.plot_dir + '/blocks/'+ block_hash + '.html')):
            self.block_file_location = str(self.plot_dir + '/blocks/'+ block_hash + '.html')
            return True
        return False

    def get_block_file_location(self):
        return self.block_file_location

    def retrieve_status_from_db(self):
        stat = ''
        stat += str(self.get_block_chain_length()) + ','
        stat += str(self.get_num_of_blocks()) + ','
        stat += str(self.get_num_of_transactions()) + ','
        stat += str(self.get_current_diff()) + ','
        stat += str(self.get_num_of_nodes()) + ','
        stat += str(self.get_min_mining_time()) + ','
        stat += str(self.get_max_mining_time()) + ','
        stat += str(self.get_avg_mining_time()) + ','
        stat += str(self.get_block_chain_memory_size())
        publish.single("bc_status", stat, hostname="localhost", port=1883)

    def send_file_error(self, err):
        publish.single("link_ref", err, hostname="localhost", port=1883)

