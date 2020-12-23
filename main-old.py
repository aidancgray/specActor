#!/usr/bin/env python3
# specActor
# 12/18/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is an actor for the BOSS specMech hardware microcontroller.

from contextlib import suppress
import asyncio


class SpecConnect:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.reader = None
        self.writer = None
        self.response = ''

    async def start_server(self):
        print(f'Opening connection with {self.ip} on port {self.port}')
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.port)

    async def send_data(self, message):
        print(f'Sent: {message!r}')
        self.writer.write(message.encode())
        await self.read_data()

    async def read_data(self):
        data = await self.reader.read(1024)
        print(f'Received: {data.decode()!r}')
        self.response = data.decode()
        while self.response[-1] != '>':
            data = await self.reader.read(1024)
            print(f'Received: {data.decode()!r}')
            self.response = self.response + data.decode()

    async def close_server(self):
        print('Closing the connection')
        await self.send_data('q\r\n')
        self.writer.close()


async def shutdown():
    print('~~~ Shutting down...')
    print('~~~ cancelling task:')
    i = 1
    for task in asyncio.all_tasks():
        print(f'~~~ {i}')
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        i += 1
    print('~~~ Done.')


async def process_command(writer, message):
    # Process the command
    await specMech.send_data(message)
    writer.write(('SPECMECH: '+repr(specMech.response)+'\r\n').encode())


async def check_data(clientWriter, message):
    # Perform error checking on the input
    # clientWriter.write(message.encode())
    check = True

    if check:
        asyncio.create_task(process_command(clientWriter, message))


async def handle_data(clientReader, clientWriter):
    dataLoop = True
    while dataLoop:
        data = await clientReader.read(100)
        message = data.decode()
        addr = clientWriter.get_extra_info('peername')
        print(f"Received {message!r} from {addr!r}")

        if message[:-2] == 'q':
            dataLoop = False
        elif message[:-2] == 'stop':
            await specMech.close_server()
        elif message[:-2] == 'start':
            await specMech.start_server()
        else:
            await check_data(clientWriter, message)
            await clientWriter.drain()

    await clientWriter.drain()
    clientWriter.close()


async def actor_server():
    server = await asyncio.start_server(handle_data, '127.0.0.1', 8887)

    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


async def main():
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
