import asyncio
import sys

from room import ChatRoom


def main(argv):
    name = argv[1] if len(argv) >= 2 else "AChat"
    port = int(argv[2]) if len(argv) >= 3 else 9999

    loop = asyncio.get_event_loop()
    chat_room = ChatRoom(name, port, loop)
    server = chat_room.run()

    loop.run_forever()


if __name__ == '__main__':
    main(sys.argv)
