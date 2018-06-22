import argparse
import logging
import os
import sys

from labchain import event
from labchain.event import EventBus
from labchain.plot import BlockchainPlotter

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# append project dir to python path
from labchain.blockchainNode import BlockChainNode  # noqa
from labchain.utility import Utility  # noqa

# set TERM environment variable if not set
if 'TERM' not in os.environ:
    os.environ['TERM'] = 'xterm-color'

CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                           'labchain', 'resources',
                                           'node_configuration.ini'))
CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), '.labchain')
DEFAULT_PLOT_DIRECTORY = os.path.join(CONFIG_DIRECTORY, 'plot')


def create_node(node_port, peer_list, plot_dir=None, plot_auto_open = False):
    event_bus = EventBus()
    if plot_dir:
        plotter = BlockchainPlotter(plot_dir, plot_auto_open)
        event_bus.register(event.EVENT_BLOCKCHAIN_INITIALIZED, plotter.plot_blockchain)
        event_bus.register(event.EVENT_BLOCK_ADDED, plotter.plot_blockchain)
    return BlockChainNode(CONFIG_FILE, event_bus, node_port, peer_list)


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
    parser.add_argument('--port', default=8080, help='The port address of the Labchain node')
    parser.add_argument('--peers', nargs='*', default=[], help='The peer list address of the Labchain node')
    parser.add_argument('--verbose', '-v', action='store_true')
    parser.add_argument('--very-verbose', '-vv', action='store_true')
    parser.add_argument('--plot', '-p', action='store_true')
    parser.add_argument('--plot-dir', default=DEFAULT_PLOT_DIRECTORY,
                        help='Enable plotting graphics to the specified dir')
    parser.add_argument('--plot-auto-open', action='store_true', help='Open plot as soon as it is created')
    return parser.parse_args()


def parse_peers(peer_args):
    result = {}
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
    if args.plot:
        plot_dir = args.plot_dir
    else:
        plot_dir = None
    node = create_node(args.port, initial_peers, plot_dir, args.plot_auto_open)
