import collections
import json
import logging
import random
import socket
import time
from copy import deepcopy
from netifaces import interfaces, ifaddresses, AF_INET, AF_INET6
from threading import Thread

import requests
from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from labchain.datastructure.block import Block
from labchain.datastructure.transaction import Transaction
from labchain.util.utility import Utility


logger = logging.getLogger(__name__)

HTTP_BAD_REQUEST = 400


class NodeNotAvailableException(Exception):
    pass


class NoPeersException(Exception):
    pass


class TransactionDoesNotExistException(Exception):
    pass


class BlockDoesNotExistException(Exception):
    pass


class NoBlockExistsInRange(Exception):
    pass


class UnexpectedResponseException(Exception):
    pass


def update(d, u):
    """Recursive dictionary update"""
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class JsonRpcClient:
    """Handle outgoing JSON-RPC calls."""

    def __init__(self):
        self.id_counter = 0

    def send(self, ip_address, port, method, params=tuple()):
        """Convert data to json and send it over the network.

        Return the answer dictionary.
        """
        url = 'http://{}:{}/'.format(ip_address, port)
        headers = {'content-type': 'application/json'}
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": self.id_counter,
        }
        logger.debug('Sending request {} to {}'.format(str(payload), url))
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            raise NodeNotAvailableException(str(e))
        logger.debug('Received response {} from {}'.format(response, url))
        self.id_counter += 1
        try:
            return response['result']
        except KeyError:
            raise UnexpectedResponseException('Unexpected response from {}: {}'.format(url, response))


class NetworkInterface:
    """Basic network interface to be used by clients."""

    def __init__(self, json_rpc_client, initial_peers):
        """

        :param initial_peers: List of IP addresses (optional with :port) of the initial peers.
        """
        self.json_rpc_client = json_rpc_client
        self.peers = {}
        for ip_address, port_map in initial_peers.items():
            for port, info in port_map.items():
                self.add_peer(ip_address, port, info)

    def sendTransaction(self, transaction):
        # send the transaction to all peers
        responses = self._bulk_send('sendTransaction', [transaction.to_dict()])
        if not responses:
            raise NoPeersException('No nodes available to send the transaction to')

    def sendBlock(self, block):
        # send the block to all peers
        responses = self._bulk_send('sendBlock', [block.to_dict()])
        if not responses:
            raise NoPeersException('No nodes available to send the block to')

    def requestTransaction(self, transaction_hash):
        """Returns the tuple (transaction, block hash of transaction)."""
        responses = self._bulk_send('requestTransaction', [transaction_hash], return_on_first_success=True)
        if responses:
            if responses[0]:
                transaction, block_hash = responses[0]
                return Transaction.from_dict(transaction), block_hash
            else:
                raise TransactionDoesNotExistException()
        else:
            raise NoPeersException('No nodes available to request the transaction from')

    def requestBlock(self, block_id):
        """Request a single block by block ID.

        Returns a list, because multiple blocks might have the same ID.
        """
        responses = self._bulk_send('requestBlock', [block_id], return_on_first_success=True)
        if responses:
            if responses[0]:
                return [Block.from_dict(block_data) for block_data in responses[0]]
            else:
                raise BlockDoesNotExistException()
        else:
            raise NoPeersException('No nodes available to request the block from')

    def requestBlockByHash(self, block_hash):
        """Request a single block by its hash value."""
        responses = self._bulk_send('requestBlockByHash', [block_hash], return_on_first_success=True)
        if responses:
            if responses[0]:
                return Block.from_dict(responses[0])
            else:
                raise BlockDoesNotExistException()
        else:
            raise NoPeersException('No nodes available to request the block from')

    def requestBlocksByHashRange(self, block_start_hash=None, block_end_hash=None):
        """Request a single block by its hash value."""
        responses = self._bulk_send('requestBlocksByHashRange', [block_start_hash, block_end_hash],
                                    return_on_first_success=True)
        res = []
        if responses:
            if len(responses) > 0:
                for block in responses[0]:
                    res.append(Block.from_dict(block))
            else:
                raise NoBlockExistsInRange()
        else:
            raise NoPeersException('No nodes available to request the block from')
        return res

    def add_peer(self, ip_address, port, info=None):
        """Add a single peer to the peer list."""
        if not Utility.is_valid_ipv4(ip_address) and not Utility.is_valid_ipv6(ip_address):
            ip_address = self.__resolve_hostname(ip_address)
        if info is None:
            info = {}
        if ip_address in self.peers and port in self.peers[ip_address] and info == self.peers[ip_address][port]:
            logger.debug('Peer {}:{} unchanged. Skipping...'.format(ip_address, str(port)))
            return
        logger.info('Peer {}:{} added/updated'.format(str(ip_address), str(port)))
        update(self.peers, {str(ip_address): {int(port): info}})
        logger.debug('My peers are now: {}'.format(str(self.peers)))

    def _add_peer_bulk(self, peer_dict):
        """Add multiple peers from a dict."""
        for ip, port_dict in peer_dict.items():
            for port, info in port_dict.items():
                self.add_peer(ip, port, info)

    def __get_shuffled_dict_items(self, dictionary):
        """Retrieve a shuffled list of peer IP addresses."""
        dict_list = list(dictionary.items())
        random.shuffle(dict_list)
        return dict_list

    def _bulk_send(self, method, params=None, return_on_first_success=False):
        """
        Send a request to all peers.

        :param method:
        :param params:
        :param return_on_first_success Terminate after the first successful response.
        :return:
        """
        if params is None:
            params = []
        responses = []
        # copy to prevent problems with concurrency
        peers = deepcopy(self.peers)
        for peer_ip, port_map in self.__get_shuffled_dict_items(peers):
            for peer_port in peers[peer_ip]:
                try:
                    response = self._send(peer_ip, peer_port, method, params)
                    responses.append(response)
                    if return_on_first_success:
                        return responses
                except NodeNotAvailableException:
                    pass
        return responses

    def _send(self, ip_address, port, method, params=None):
        """
        Wrapper around the JSON-RPC client for removing unresponsive peers.

        :param ip_address:
        :param port:
        :param method:
        :param params:
        :return:
        """
        if params is None:
            params = []
        try:
            return self.json_rpc_client.send(ip_address, port, method, params)
        except NodeNotAvailableException as e:
            logger.info('Peer {}:{} went offline. Removing from peer list...'.format(ip_address, port))
            self._remove_peer(ip_address, port)
            raise e

    def _remove_peer(self, host, port):
        """Remove a peer from the peer list."""
        if host in self.peers and port in self.peers[host]:
            del self.peers[host][port]
            # remove address if last port was removed
            if not self.peers[host]:
                del self.peers[host]

    @staticmethod
    def __resolve_hostname(ip_address):
        return socket.gethostbyname(ip_address)


class ServerNetworkInterface(NetworkInterface):
    """Advanced network interface for additional server-to-server communication."""

    def __init__(self, json_rpc_client, initial_peers, crypto_helper,
                 on_block_received_callback,
                 on_transaction_received_callback,
                 get_block_callback,
                 get_block_by_hash_callback,
                 get_transaction_callback,
                 get_blocks_by_hash_range, port=8080, block_cache_size=1000, transaction_cache_size=1000):
        """
        :param json_rpc_client: A JsonRpcClient instance.
        :param initial_peers: A dict structured like {'<ip1>': {'port': <port1>}, ...}.
        :param on_block_received_callback: A callable accepting a Block instance as argument.
        :param on_transaction_received_callback: A callable accepting a Transaction instance as argument.
        :param get_block_callback: A callable that gets a block ID and returns the corresponding Block instance or None.
        :param get_transaction_callback: A callable that gets a transaction hash and returns the corresponding
                                            Transaction instance or None.
        :param port: The port number to listen on.
        """
        super().__init__(json_rpc_client, initial_peers)
        self.crypto_helper = crypto_helper
        self.on_block_received_callback = on_block_received_callback
        self.on_transaction_received_callback = on_transaction_received_callback
        self.get_block_callback = get_block_callback
        self.get_block_by_hash_callback = get_block_by_hash_callback
        self.get_transaction_callback = get_transaction_callback
        self.get_blocks_by_hash_range_callback = get_blocks_by_hash_range
        self.port = int(port)
        self.block_cache = []
        self.block_cache_size = block_cache_size
        self.transaction_cache = []
        self.transaction_cache_size = transaction_cache_size

    def update_peer_lists(self):
        """Get new peer lists from all peers."""
        logger.info('Updating peers...')
        responses = self._bulk_send('getPeers')
        new_peers = {}
        for response in responses:
            response = self.__filter_own_address(response)
            self._add_peer_bulk(response)
        self.peers = update(self.peers, new_peers)
        DashBoardDB.instance().change_num_of_nodes(len(self.peers) + 1)
        DashBoardDB.instance().retrieve_status_from_db()
        logger.info('My peers are now: {}'.format(str(self.peers)))

    def advertise_to_peers(self):
        """Ask peers to become part of their peer list."""
        if not self.peers:
            logger.warning('Cannot advertise: No peers in peer list!')
            return
        logger.debug('Advertising myself to peers...')
        self._bulk_send('advertisePeer', [self.port])

    def poll_update_peer_lists(self, poll_interval=10):
        logger.info('Start polling for peer lists...')
        while True:
            logger.debug('Performing next peer list polling iteration...')
            self.update_peer_lists()
            self.advertise_to_peers()
            logger.debug('Peer list polling done. Waiting for {} seconds.'.format(poll_interval))
            time.sleep(poll_interval)

    def start_listening(self, threaded=True):
        """Start listening for incoming HTTP JSON-RPC calls."""
        logger.debug('Starting web server...')
        run_simple('0.0.0.0', self.port, self.application, threaded=threaded)

    @Request.application
    def application(self, request):
        """Define the JSON-RPC callbacks and handle an incoming request."""
        dispatcher['getPeers'] = self.__handle_get_peers
        dispatcher['advertisePeer'] = self.__handle_advertise_peer
        dispatcher['sendBlock'] = self.__handle_send_block
        dispatcher['sendTransaction'] = self.__handle_send_transaction
        dispatcher['requestBlock'] = self.__handle_request_block
        dispatcher['requestBlockByHash'] = self.__handle_request_block_by_hash
        dispatcher['requestTransaction'] = self.__handle_request_transaction
        dispatcher['requestBlocksByHashRange'] = self.__handle_request_blocks_by_hash_range

        # insert IP address of peer if advertise peer is called
        try:
            request_body_dict = json.loads(request.data.decode())
        except ValueError:
            return Response(status=HTTP_BAD_REQUEST)
        if request_body_dict['method'] == 'advertisePeer':
            if 'params' not in request_body_dict:
                request_body_dict['params'] = [6666]
            request_body_dict['params'].insert(0, request.remote_addr)
        request.data = json.dumps(request_body_dict)

        response = JSONRPCResponseManager.handle(
            request.data, dispatcher)
        return Response(response.json, mimetype='application/json')

    def __handle_get_peers(self):
        return self.peers

    def __handle_advertise_peer(self, remote_address, port):
        self.add_peer(remote_address, port)
        return True

    def __handle_send_block(self, block_data):
        block = Block.from_dict(block_data)
        block_initially_in_chain = block in self.get_block_callback(block.block_id)
        self.on_block_received_callback(block)
        if block not in self.get_block_callback(block.block_id):
            # if still not in chain, the bock must be invalid
            self.__add_block_to_cache(block)
        if not block_initially_in_chain and not self.__block_in_cache(block):
            logger.debug('Broadcasting block: {}'.format(str(block)))
            self._call_threaded(self.__send_block_safe, [block])
        else:
            logger.debug('Block already present. Skipping propagation: {}'.format(block))

    def __send_block_safe(self, block):
        try:
            self.sendBlock(block)
        except NoPeersException:
            pass

    def __handle_send_transaction(self, transaction_data):
        transaction = Transaction.from_dict(transaction_data)
        transaction_hash = self.crypto_helper.hash(transaction.get_json())
        transaction_in_pool, _ = self.get_transaction_callback(transaction_hash)
        self.on_transaction_received_callback(transaction)
        if not self.get_transaction_callback(transaction_hash)[0]:
            # if transaction still not present, it must have been delined
            self.__add_transaction_to_cache(transaction)
        if not transaction_in_pool == transaction and not self.__transaction_in_cache(transaction):
            logger.debug('Broadcasting transaction: {}'.format(str(transaction)))
            logger.debug('Broadcasting transaction hash: ' + str(transaction_hash))
            try:
                self._call_threaded(self.sendTransaction, [transaction])
            except NoPeersException:
                pass

    def __handle_request_block(self, block_id):
        blocks = self.get_block_callback(block_id)
        if blocks:
            return [block.to_dict() for block in blocks]
        return []

    def __handle_request_block_by_hash(self, block_hash):
        block = self.get_block_by_hash_callback(block_hash)
        if block:
            return block.to_dict()
        return []

    def __handle_request_blocks_by_hash_range(self, block_hash_start_hash=None, block_hash_end_hash=None):
        blocks = self.get_blocks_by_hash_range_callback(block_hash_start_hash, block_hash_end_hash)
        if blocks:
            return [block.to_dict() for block in blocks]
        return []

    def __handle_request_transaction(self, transaction_hash):
        transaction, block_hash = self.get_transaction_callback(transaction_hash)
        if transaction:
            return transaction.to_dict(), block_hash
        return None

    def __filter_own_address(self, peers):
        """Filter entries with own IP address and port."""
        my_addresses = self.__ip4_addresses() + self.__ip6_addresses()
        my_port = str(self.port)
        for my_address in my_addresses:
            if my_address in peers and my_port in peers[my_address]:
                del (peers[my_address][my_port])
                logger.debug('Filtered own address {}:{} from received peers'.format(my_address, my_port))
                # remove address if last port was removed
                if not peers[my_address]:
                    del (peers[my_address])
        return peers

    @staticmethod
    def __ip4_addresses():
        ip_list = []
        for interface in interfaces():
            addresses = ifaddresses(interface)
            if AF_INET in addresses:
                for link in addresses[AF_INET]:
                    ip_list.append(link['addr'])
        return ip_list

    @staticmethod
    def __ip6_addresses():
        ip_list = []
        for interface in interfaces():
            addresses = ifaddresses(interface)
            if AF_INET6 in addresses:
                for link in addresses[AF_INET6]:
                    ip_list.append(link['addr'])
        return ip_list

    @staticmethod
    def _call_threaded(func, args):
        thread = Thread(target=func, args=args)
        thread.start()

    def __add_block_to_cache(self, block):
        if not self.__block_in_cache(block):
            self.block_cache.append(block)
        if len(self.block_cache) > self.block_cache_size:
            self.block_cache.pop(0)

    def __block_in_cache(self, block):
        return block in self.block_cache

    def __add_transaction_to_cache(self, transaction):
        if not self.__transaction_in_cache(transaction):
            self.transaction_cache.append(transaction)
        if len(self.transaction_cache) > self.transaction_cache_size:
            self.transaction_cache.pop(0)

    def __transaction_in_cache(self, transaction):
        return transaction in self.transaction_cache


ClientNetworkInterface = NetworkInterface
