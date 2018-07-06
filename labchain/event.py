import logging
from threading import Thread

EVENT_BLOCKCHAIN_INITIALIZED = 'blockchain.initialized'
EVENT_BLOCK_ADDED = 'blockchain.block_added'
logger = logging.getLogger(__name__)


class EventBus:
    """A simple event bus implementation."""

    def __init__(self):
        self.registry = {}

    def register(self, event, callback):
        """Register a new event."""
        logger.debug('Registering callback {} for event {}'.format(callback, event))
        if event not in self.registry:
            self.registry[event] = []
        self.registry[event].append(callback)

    def fire(self, event, data):
        """Fire an event."""
        if event not in self.registry:
            return
        for callback in self.registry[event]:
            thread = Thread(target=callback, args=(data,))
            thread.start()
