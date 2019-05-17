import logging
import socket
import uuid

from zeroconf import ServiceInfo, Zeroconf

logger = logging.getLogger(__name__)


class ServiceListener:

    def __init__(self, callback_function):
        self.callback = callback_function

    def remove_service(self, zeroconf: Zeroconf, type, name):
        logger.debug("Service %s removed" % (name,))

    def add_service(self, zeroconf: Zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        logger.debug("Service %s added, service info: %s" % (name, info))
        if self.callback is not None and info is not None:
            self.callback(info)


class PeerDiscoverySystem:

    def __init__(self, ip: str, port: int, callback_function=None):
        self.type = "_labchain._tcp.local."
        nonce = uuid.uuid1().hex[:10]
        self.name = "LabChain Node {}._labchain._tcp.local.".format(nonce)
        self.ip = socket.inet_aton(ip)
        self.port = port
        self.desc = {}
        self.serviceinfo = ServiceInfo(self.type, self.name, self.ip,
                                       self.port, 0, 0, self.desc)
        self.zeroconf = Zeroconf()
        self.browser = None
        self.listener = ServiceListener(callback_function=callback_function)

    def register_service(self):
        ip: str = socket.inet_ntoa(self.ip)
        logger.debug('Registering service: {} for host with IP: {} and port: {}'
                     .format(self.type, ip, str(self.port)))
        self.zeroconf.register_service(self.serviceinfo)

    def stop_service(self):
        ip: str = socket.inet_ntoa(self.ip)
        logger.debug(
            'Unregistering service: {} for host with IP: {} and port: {}'
            .format(self.type, ip, str(self.port)))
        self.zeroconf.unregister_service(self.serviceinfo)
        self.zeroconf.close()

    def start_service_listener(self):
        self.zeroconf.add_service_listener(type_=self.type,
                                           listener=self.listener)

    def __del__(self):
        self.stop_service()
