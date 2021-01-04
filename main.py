#!/usr/bin/env python3
# specActor
# 12/18/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is an actor for the BOSS specMech hardware microcontroller.

from clu import LegacyActor, command_parser
from contextlib import suppress
import asyncio
import click


@command_parser.command()
@click.argument('DATA', type=str)
async def talk(command, data):
    """
    'Talk' command to send data string directly as-is to the specMech

    Args:
        data (str): The string to send to specMech
    """
    dataTemp = data+'\r'
    await specMech.send_data(dataTemp)

    if '$S2ERR*24' in specMech.response:
        messageCode = 'f'
    else:
        messageCode = ':'

    command.write(messageCode, SPECMECH=f'{repr(specMech.response)}')
    command.finish()


class SpecActor(LegacyActor):
    """
    A legacy-style actor that accepts commands to control the specMech

    """
    def __init__(self):
        super().__init__(name='spec_actor',
                         host='localhost', port=9999,
                         version='0.1.0')


class SpecConnect:
    """
    A class for connecting to & communicating with the specMech.

    Args:
        ip (str): the IP address of the specMech
        port (int): the port # the specMech is listening on
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.reader = None
        self.writer = None
        self.response = ''

    async def start_server(self):
        """
        Opens a connection with the given ip & port

        """
        print(f'Opening connection with {self.ip} on port {self.port}')
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port)

    async def send_data(self, message):
        """
        Sends the given string to the specMech and then awaits a response.
        Args:
            message (str): A string that is sent to specMech

        """
        print(f'Sent: {message!r}')
        self.writer.write(message.encode())
        await self.read_data()

    async def read_data(self):
        """
        Awaits responses from specMech until the EOM character '>' is seen.

        The data received from specMech is added to the response variable.

        """
        data = await self.reader.read(1024)
        print(f'Received: {data.decode()!r}')
        self.response = data.decode()
        while self.response[-1] != '>':
            data = await self.reader.read(1024)
            print(f'Received: {data.decode()!r}')
            self.response = self.response + data.decode()

    async def close_server(self):
        """
        Closese the connection with specMech

        """
        print('Closing the connection')
        await self.send_data('q\r\n')
        self.writer.close()


async def actor_server():
    """
    Async method to serve up the specActor server.

    """
    spec_actor = await SpecActor().start()
    await spec_actor.run_forever()


async def main():
    """
    Runs the server and client coroutines

    """
    with suppress(asyncio.CancelledError):
        taskServer = asyncio.create_task(specMech.start_server())
        taskClient = asyncio.create_task(actor_server())
        await asyncio.gather(taskServer, taskClient)

if __name__ == "__main__":
    specMech = SpecConnect('127.0.0.1', 8888)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('~~~Keyboard Interrupt~~~')
    except Exception as e:
        print(f'Unexpected Error: {e}')
