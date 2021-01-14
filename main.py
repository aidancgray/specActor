#!/usr/bin/env python3
# specActor
# 12/18/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is an actor for the BOSS specMech hardware microcontroller.

from clu import LegacyActor, command_parser
from contextlib import suppress
import clu
import asyncio
import click
import warnings


@command_parser.command()
async def test(command, msg):
    """
    'test' command is just for testing
    """
    messageCode = ':'
    command.write(messageCode, text=f'{msg}')


@command_parser.command()
async def ACK(command):
    """
    'ACK' command acknowledges the specMech has rebooted and informs the user
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        dataTemp = '!\r'
        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command()
@click.argument('DATA', type=str)
async def talk(command, data):
    """
    'talk' command to send data string directly as-is to the specMech

    Args:
        data (str): The string to send to specMech
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        dataTemp = data+'\r'
        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
        else:
            messageCode = ':'

        command.write(messageCode, SPECMECH=f'{repr(specActor.response)}')


@command_parser.command()
@click.argument('OFFSET', type=int)
async def focus(command, offset):
    """
    'focus' command to send an offset to the specMech's 3 collimator motors

    Args:
        offset (int): Piston all collimator motors together by this value
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        dataTemp = f'mp{offset}\r'
        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command()
@click.argument('TIME', type=str)
async def set_time(command, time):
    """
    'set-time' command to set the clock time of the specMech

    Args:
        time (str): The clock time in format: YYYY-MM-DDThh:mm:ssZ
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        dataTemp = f'st{time}\r'
        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command()
@click.argument('EXPOSURE', type=click.Choice(['left', 'right', 'start', 'end']),
                default='start')
async def expose(command, exposure):
    """
    'expose' command to tell the specMech which Hartmann Doors
    to open or close.

    Args:
        exposure (str): This can be left/right/start/end. The first 3 open
                        either the left, right, or both doors. The last closes
                        everything that is open.
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        if exposure == 'left':
            dataTemp = 'el\r'
        elif exposure == 'right':
            dataTemp = 'er\r'
        elif exposure == 'start':
            dataTemp = 'es\r'
        elif exposure == 'end':
            dataTemp = 'ee\r'
        else:
            dataTemp = 'es\r'

        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command(name='open')
@click.argument('DOOR', type=click.Choice(['left', 'right', 'shutter']),
                default='shutter')
async def openDoor(command, door):
    """
    'open' command opens left, right, or shutter

    Args:
        door (str): This can be left/right/shutter.
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        if door == 'left':
            dataTemp = 'ol\r'
        elif door == 'right':
            dataTemp = 'or\r'
        elif door == 'shutter':
            dataTemp = 'os\r'
        else:
            dataTemp = 'os\r'

        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command(name='close')
@click.argument('DOOR', type=click.Choice(['left', 'right', 'shutter']),
                default='shutter')
async def closeDoor(command, door):
    """
    'close' command closes left, right, or shutter

    Args:
        door (str): This can be left/right/shutter.
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        if door == 'left':
            dataTemp = 'cl\r'
        elif door == 'right':
            dataTemp = 'cr\r'
        elif door == 'shutter':
            dataTemp = 'cs\r'
        else:
            dataTemp = 'cs\r'

        specActor.response = ''
        await specActor.send_data(dataTemp)

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = ':'
            command.write(messageCode, text='OK')


@command_parser.command()
async def status(command):
    """
    'status' command queries specMech for all status responses
    """
    if '>' not in specActor.response:
        messageCode = 'f'
        command.write(messageCode, text='WAIT FOR >')
    else:
        specActor.response = ''
        await specActor.send_data('rs\r')

        if '$S2ERR*24' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='ERR')
        elif '!' in specActor.response:
            messageCode = 'f'
            command.write(messageCode, text='SPECMECH HAS REBOOTED')
        else:
            messageCode = 'i'

            # Parse the status response. Write a reply to the user for each relevant
            #  status string. This may be changed later.
            statusList = specActor.response.split("\r\n")
            strpList = []

            for n in statusList:  # separate the individual status responses
                if '$S2' in n:
                    tempStr1 = n[3:]  # remove '$S2'
                    tempStr2 = tempStr1.split('*')[0]  # remove the NMEA checksum
                    strpList.append(tempStr2)

            finalList = []
            for m in strpList:  # for each status response, split up the components
                finalList.append(m.split(','))

            # initialize all keyword vars, just to be safe
            btm = mra = mrb = mrc = env0t = env0h = env1t = env1h = env2t = env2h = ''
            env3t = env3h = ionr = ionb = accx = accy = accz = pnus = pnul = pnur = ''
            pnup = tim = ver = ''

            for stat in finalList:  # establish each keyword=value pair
                if stat[0] == 'BTM':
                    btm = stat[1]

                elif stat[0] == 'MRA':
                    mra = stat[1]

                elif stat[0] == 'MRB':
                    mrb = stat[1]

                elif stat[0] == 'MRC':
                    mrc = stat[1]

                elif stat[0] == 'ENV':
                    env0t = stat[1]
                    env0h = stat[2]
                    env1t = stat[4]
                    env1h = stat[5]
                    env2t = stat[7]
                    env2h = stat[8]
                    env3t = stat[10]
                    env3h = stat[11]

                elif stat[0] == 'ION':
                    ionr = stat[1]
                    ionb = stat[3]

                elif stat[0] == 'ACC':
                    accx = stat[1]
                    accy = stat[2]
                    accz = stat[3]

                elif stat[0] == 'PNU':
                    # change the c/o/t and 0/1 responses of specMech
                    # to something more readable
                    if stat[1] == 'c':
                        pnus = 'closed'
                    elif stat[1] == 'o':
                        pnus = 'open'
                    else:
                        pnus = 'transiting'

                    if stat[3] == 'c':
                        pnul = 'closed'
                    elif stat[3] == 'o':
                        pnul = 'open'
                    else:
                        pnul = 'transiting'

                    if stat[5] == 'c':
                        pnur = 'closed'
                    elif stat[5] == 'o':
                        pnur = 'open'
                    else:
                        pnur = 'transiting'

                    if stat[7] == '0':
                        pnup = 'off'
                    elif stat[7] == '1':
                        pnup = 'on'

                elif stat[0] == 'TIM':
                    tim = stat[1]

                elif stat[0] == 'VER':
                    ver = stat[1]

            command.write(messageCode,
                          systemInfo=f'(bootTime={btm}, clockTime={tim}, version={ver})')

            command.write(messageCode,
                          motorPositions=f'(motorA={mra}, motorB={mrb}, motorC={mrc})')

            command.write(messageCode,
                          environments=f'(Temperature0={env0t}, Humidity0={env0h}, '
                                       f'Temperature1={env1t}, Humidity1={env1h}, '
                                       f'Temperature2={env2t}, Humidity2={env2h}, '
                                       f'Temperature3={env3t}, Humidity3={env3h})')

            command.write(messageCode,
                          ionPumpVoltages=f'(redDewarVoltage={ionr}, blueDewarVoltage={ionb})')

            command.write(messageCode,
                          accelerometer=f'(xAxis={accx}, yAxis={accy}, zAxis={accz})')

            command.write(messageCode,
                          pneumatics=f'(shutter={pnus}, leftHartmann={pnul}, rightHartmann={pnur}, airPressure={pnup})')

            command.finish()


class SpecActor(LegacyActor):
    """
    A legacy-style actor that accepts commands to control the specMech
    """
    def __init__(self):
        super().__init__(name='spec_actor',
                         host='localhost',
                         port=9999,
                         version='0.1.0')

        self.reader = None
        self.writer = None
        self.response = '>'

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
        self.reader, self.writer = await asyncio.open_connection(
            self.ip, self.specMechPort)

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
        dataRaw = await self.reader.read(1024)
        dataB = bytearray(dataRaw)

        # Continue accepting responses until '>' is received
        while bytearray(b'>') not in dataB:
            dataRaw = await self.reader.read(1024)
            dataB.extend(bytearray(dataRaw))

        self.response = dataB.decode('utf-8', 'ignore')
        print(f'Received: {self.response}')

    async def close_server(self):
        """
        Closes the connection with specMech
        """
        print('Closing the connection')
        await self.send_data('q\r\n')
        self.writer.close()


async def actor_server():
    """
    Async method to serve up the specActor server.
    """
    spec_actor = await specActor.start()
    await spec_actor.run_forever()


async def main():
    """
    Runs the server and client coroutines
    """
    with suppress(asyncio.CancelledError):
        # taskClient = asyncio.create_task(actor_server())
        # await asyncio.gather(taskClient)
        await actor_server()

if __name__ == "__main__":
    specActor = SpecActor()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('~~~Keyboard Interrupt~~~')
    except Exception as e:
        print(f'Unexpected Error: {e}')
