import asyncio
from itertools import chain


class ChatProtocol(asyncio.Protocol):
    LINE_DELIMITER = '\n'

    def __init__(self, chat_room):
        self._chat_room = chat_room
        self._username = None
        self._transport = None
        self._buffer = []

    def connection_made(self, transport):
        self._transport = transport
        self._write_line('Welcome to {}'.format(self._chat_room.name))
        self._write('Enter your name: ')

    def data_received(self, raw_data):
        try:
            data = raw_data.decode('utf-8')
        except UnicodeDecodeError as e:
            self._write_line(str(e).encode('utf-8'))
        else:
            for line in self._accumulated_lines(data):
                self._handle(line)

    def connection_lost(self, exc):
        if self._username:
            self._unregister_user()

    def _write_line(self, line):
        self._write(line)
        self._write(self.LINE_DELIMITER)

    def _write(self, text: str):
        self._transport.write(text.encode('utf-8'))

    def _register_user(self, line: str):
        username = line.strip()
        if self._chat_room.register_user(username, self._transport):
            self._username = username
        else:
            self._write_line('Username {} is unavailable{}'.format(username, self.LINE_DELIMITER))

    def _unregister_user(self):
        if self._username is not None:
            self._chat_room.unregister_user(self._username)

    def _accumulated_lines(self, data):
        self._buffer.append(data)
        while True:
            tail, newline, head = self._buffer[-1].partition(self.LINE_DELIMITER)
            if not newline:
                break

            line = ''.join(chain(self._buffer[:-1], (tail,)))
            self._buffer = [head]
            yield line

    def _handle(self, line):
        if self._username is None:
            self._register_user(line)
        else:
            self._chat_room.message_received(self._username, line)
