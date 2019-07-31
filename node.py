import argparse
import logging
import os
import socket
import sys

# append project dir to python path
from labchain.blockchainNode import BlockChainNode
from labchain.util.configReader import ConfigReader
from labchain.util.utility import Utility

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'labchain', 'resources',
                                           'node_configuration.ini'))
CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
DEFAULT_PLOT_DIRECTORY = os.path.join(CONFIG_DIRECTORY, 'plot')


def create_node(node_ip, node_port, peer_list, peer_discovery):
    return BlockChainNode(CONFIG_FILE, node_ip, node_port, peer_list,
                          peer_discovery)


def setup_logging(verbose, very_verbose):
    if very_verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_args():
    parser = argparse.ArgumentParser(description='CLI node for Labchain.')
    parser.add_argument('--port', default=8080,
                        help='The port address of the Labchain node')
    parser.add_argument('--peers', nargs='*', default=[],
                        help='The peer list address of the Labchain node')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--very-verbose', '-vv', action='store_true')
    parser.add_argument('--peer-discovery', action='store_true')
    parser.add_argument('--drop_db', '-d', action='store_true')
    parser.add_argument('--localhost', action='store_true')
    return parser.parse_args()


def get_private_ip():
    own_ip = None
    try:
        config = ConfigReader(CONFIG_FILE)
        resolver = config.get_config(section="NETWORK", option="DNS_CLIENT")

        # Get own private IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((resolver, 53))
        own_ip = s.getsockname()[0]
    except Exception as e:
        logging.error(str(e))
    return own_ip if own_ip is not None else "127.0.0.1"


def parse_peers(peer_args):
    result = {}
    try:
        config = ConfigReader(CONFIG_FILE)
        default_port = config.get_config(section="NETWORK", option="PORT",
                                         fallback=8080)
        default_port = str(default_port)

        own_ip = get_private_ip()
    except Exception as e:
        logging.error(str(e))

    for peer_str in peer_args:
        host, port = peer_str.split(':')
        if host not in result:
            result[host] = {}
        result[host][port] = {}
    return result


if __name__ == '__main__':
    test = sys.argv
    args = parse_args()
    setup_logging(args.verbose, args.very_verbose)
    initial_peers = parse_peers(args.peers)
    Utility.print_labchain_logo()

    ip = '127.0.0.1' if args.localhost else get_private_ip()

    if (args.drop_db):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './labchain/resources/labchaindb.sqlite'))
        if os.path.exists(db_path):
            os.remove(db_path)

    node = create_node(ip, args.port, initial_peers, args.peer_discovery)
