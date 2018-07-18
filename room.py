from asyncio import AbstractEventLoop
from asyncio import Transport

from protocol import ChatProtocol


class ChatRoom:
    def __init__(self, name: str, port: int, loop: AbstractEventLoop):
        self._name = name
        self._port = port
        self._loop = loop
        self._username_transports = {}

    @property
    def name(self):
        return self._name

    def run(self):
        coro = self._loop.create_server(
            protocol_factory=lambda: ChatProtocol(self),
            host='',
            port=self._port)

        self._loop.run_until_complete(coro)

    def users(self):
        return self._username_transports.keys()

    def register_user(self, username, transport):
        if username in self.users():
            return False
        self._username_transports[username] = transport
        self._broadcast(
            'User {} arrived{}'.format(
                username, ChatProtocol.LINE_DELIMITER))
        return True

    def unregister_user(self, username):
        del self._username_transports[username]
        self._broadcast(
            'User {} departed{}'.format(
                username, ChatProtocol.LINE_DELIMITER))

    def message_received(self, username, message):
        self._broadcast(
            '{}: {}{}'.format(username, message, ChatProtocol.LINE_DELIMITER))

    def _broadcast(self, message):
        transport: Transport
        for transport in self._username_transports.values():
            transport.write(message.encode('utf-8'))
