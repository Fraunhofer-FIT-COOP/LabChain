import argparse
import signal
import logging
import os
import socket

# append project dir to python path
from labchain.blockchainNode import BlockChainNode
from labchain.util.configReader import ConfigReader
from labchain.util.utility import Utility
from labchain.util.benchmarkEngine import BenchmarkEngine

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                           'labchain', 'resources',
                                           'node_configuration.ini'))
CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
DEFAULT_PLOT_DIRECTORY = os.path.join(CONFIG_DIRECTORY, 'plot')


def create_node(node_ip, malicious, node_port, peer_list, peer_discovery, cors):
    return BlockChainNode(CONFIG_FILE, malicious, node_ip, node_port, peer_list,
                          peer_discovery, cors=cors)


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
    parser.add_argument('--benchmark', '-b', default="",
                        help='Outputs detailed process information to enable benchmarking the implementation')
    parser.add_argument('--verbose', '-v', action='store_true', help="Debug level INFO")
    parser.add_argument('--very-verbose', '-vv', action='store_true', help="Debug level DEBUG")
    parser.add_argument('--peer-discovery', action='store_true', help="Use zero-conf service to connect to nodes in the same network")
    parser.add_argument('--drop_db', '-d', action='store_true', help="Delete database")
    parser.add_argument('--localhost', action='store_true', help="Start as localhost")
    parser.add_argument('--cors', default="", action="store", help="Set CORS headers for the networking component")
    parser.add_argument('--malicious', '-m', action='store_true')
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

    for peer_str in peer_args:
        host, port = peer_str.replace("\"", "").replace("'", "").split(':')
        if host not in result:
            result[host] = {}
        result[host][port] = {}
    return result


if __name__ == '__main__':
    args = parse_args()
    setup_logging(args.verbose, args.very_verbose)
    initial_peers = parse_peers(args.peers)
    BenchmarkEngine.setFilepath(args.benchmark)

    def gracefulKill(signum, frame):
        BenchmarkEngine.write()
        sys.exit()

    signal.signal(signal.SIGINT, gracefulKill)
    signal.signal(signal.SIGTERM, gracefulKill)

    Utility.print_labchain_logo()

    ip = '127.0.0.1' if args.localhost else get_private_ip()

    if (args.drop_db):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './labchain/resources/labchaindb.sqlite'))
        if os.path.exists(db_path):
            os.remove(db_path)

    cors = args.cors.replace("\"", "")

    node = create_node(ip, args.malicious, args.port, initial_peers, args.peer_discovery, cors)
