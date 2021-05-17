import clu
from clu import LegacyActor
import asyncio
import telnetlib3
import warnings


class SpecActor(LegacyActor):
    """
    A legacy-style actor that accepts commands to control the specMech
    """
    def __init__(self, log):
        super().__init__(name='spec_actor',
                         host='localhost',
                         port=9999,
                         version='0.1.0')

        self.reader = None
        self.writer = None
        self.response = '>'
        self.reboot = False
        self.commandNumber = 0
        self.commandQueue = []
        self.log = log

        # For the specMech emulator connection
        self.ip = '127.0.0.1'
        self.specMechPort = 8888

        # For the real specMech connection
        # self.ip = 'specmech.mywire.org'
        # self.specMechPort = 23

    async def start(self):
        """Starts the server and the Tron client connection."""

        await self._server.start()
        self.log.info(f'running TCP server on {self.host}:{self.port}')

        # Start tron connection
        try:
            if self.tron:
                await self.tron.start()
                self.log.info('started tron connection at '
                              f'{self.tron.host}:{self.tron.port}')
            else:
                warnings.warn('starting LegacyActor without Tron connection.',
                              clu.CluWarning)
        except (ConnectionRefusedError, OSError) as ee:
            warnings.warn(f'connection to tron was refused: {ee}. '
                          'Some functionality will be limited.', clu.CluWarning)

        self.timed_commands.start()

        await self.start_server()

        return self

    async def start_server(self):
        """
        Opens a connection with the given ip & port
        """
        print(f'Opening connection with {self.ip} on port {self.specMechPort}')

        loop = asyncio.get_running_loop()
        loop.set_exception_handler(self.log.asyncio_exception_handler)

        telTask = loop.create_task(telnetlib3.open_connection(self.ip, self.specMechPort))
        self.reader, self.writer = await telTask

    async def send_data(self, message):
        """
        Sends the given string to the specMech and then awaits a response.

        Args:
            message (str): A string that is sent to specMech
        """
        # Only send '!\r' to acknowledge a reboot
        if message == '!':
            messageFinal = message + '\r'
        else:
            # Increment commandNumber, add the command + id to the queue
            self.commandNumber += 1
            self.commandQueue.append({'id': self.commandNumber, 'command': message})

            # Add command identifier to the message
            messageFinal = message + ';' + str(self.commandNumber) + '\r'

        # Send the message
        print(f'Sent: {messageFinal!r}')
        self.writer.write(messageFinal)
        await self.read_data()

    async def read_data(self):
        """
        Awaits responses from specMech until the EOM character '>' is seen.
        The data received from specMech is added to the response variable.
        """
        dataRaw = await self.reader.read(1024)

        # Continue accepting responses until '>' is received
        while '>' not in dataRaw and '!' not in dataRaw:
            dataRawTmp = await self.reader.read(1024)
            dataRaw = dataRaw + dataRawTmp

        if dataRaw == '!':
            self.reboot = True
        else:
            self.reboot = False

        self.response = dataRaw
        print(f'Received: {self.response!r}')
        await self.pop_from_queue()

    async def pop_from_queue(self):
        statusList = self.response.split("\r\x00\n")
        # print('statusList = ', statusList)
        strpList = []

        for n in statusList:  # separate the individual status responses
            if '$S1' in n:
                tempStr1 = n[3:]  # remove '$S1'
                tempStr2 = tempStr1.split('*')[0]  # remove the NMEA checksum
                strpList.append(tempStr2)

        finalList = []
        for m in strpList:  # for each status response, split up the components
            finalList.append(m.split(','))

        if len(finalList) != 0:
            try:
                tmpCMDid = int(finalList[0][len(finalList[0])-1])  # get last part of response
            except ValueError:
                print('Internal Command Queue Error')

            print(self.commandQueue)
            n = 0
            for cmd in self.commandQueue:
                if cmd['id'] == tmpCMDid:
                    self.commandQueue.pop(n)
                n += 1
            print(self.commandQueue)

    async def close_server(self):
        """
        Closes the connection with specMech
        """
        print('Closing the connection')
        await self.send_data('q\r\n')
        self.writer.close()
