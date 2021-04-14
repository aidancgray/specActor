#!/usr/bin/env python3
# specActor
# 12/18/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is an actor for the BOSS specMech hardware microcontroller.

import clu
from clu import LegacyActor, command_parser
from contextlib import suppress

from sdsstools import get_logger

import telnetlib3
import asyncio
import click
import warnings


NAME = 'sdss-boss-specActor'
log = get_logger(NAME)
log.start_file_logger('~/Desktop/specActor.log')


@command_parser.command()
async def test(command, msg):
    """
    'test' command for testing out stuff
    """
    messageCode = ':'
    command.write(messageCode, text=f'{msg}')


@command_parser.command()
async def command_list(command):
    """
    'command-list' prints the list of currently running commands
    """
    messageCode = ':'
    command.write(messageCode, commands=f'{specActor.commandQueue!r}')


@command_parser.command()
async def ack(command):
    """
    'ACK' command acknowledges the specMech has rebooted and informs the user
    """
    specActor.response = ''
    await specActor.send_data('!')

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
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
    specActor.response = ''
    await specActor.send_data(data)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, SPECMECH=f'{repr(specActor.response)}')
    elif specActor.reboot:
        messageCode = 'f'
        command.write(messageCode, text='SPECMECH HAS REBOOTED')
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
    dataTemp = f'mp{offset}'
    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
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
        time (str): The clock time in format: YYYY-MM-DDThh:mm:ss
    """
    dataTemp = f'st{time}'
    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
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
    if exposure == 'left':
        dataTemp = 'el'
    elif exposure == 'right':
        dataTemp = 'er'
    elif exposure == 'start':
        dataTemp = 'es'
    elif exposure == 'end':
        dataTemp = 'ee'
    else:
        dataTemp = 'es'

    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
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
    if door == 'left':
        dataTemp = 'ol'
    elif door == 'right':
        dataTemp = 'or'
    elif door == 'shutter':
        dataTemp = 'os'
    else:
        dataTemp = 'os'

    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
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
    if door == 'left':
        dataTemp = 'cl'
    elif door == 'right':
        dataTemp = 'cr'
    elif door == 'shutter':
        dataTemp = 'cs'
    else:
        dataTemp = 'cs'

    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
        messageCode = 'f'
        command.write(messageCode, text='SPECMECH HAS REBOOTED')
    else:
        messageCode = ':'
        command.write(messageCode, text='OK')


@command_parser.command()
@click.argument('STAT', type=click.Choice(['time', 'version', 'env', 'vac', '']),
                default='')
async def status(command, stat):
    """
    'status' command queries specMech for all status responses
    """
    if stat == 'time':
        dataTemp = 'rt'
    elif stat == 'version':
        dataTemp = 'rV'
    elif stat == 'env':
        dataTemp = 're'
    elif stat == 'vac':
        dataTemp = 'rv'
    else:
        dataTemp = 'rs'

    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S2ERR*24' in specActor.response:
        log.error("Unknown error response from specMech")
        messageCode = 'f'
        command.write(messageCode, text='ERR')
    elif specActor.reboot:
        messageCode = 'f'
        command.write(messageCode, text='SPECMECH HAS REBOOTED')
    else:
        messageCode = 'i'

        # Parse the status response. Write a reply to the user for each relevant
        #  status string. This may be changed later.
        statusList = specActor.response.split("\r\x00\n")
        strpList = []

        for n in statusList:  # separate the individual status responses
            if '$S2' in n:
                tempStr1 = n[3:]  # remove '$S2'
                tempStr2 = tempStr1.split('*')[0]  # remove the NMEA checksum
                strpList.append(tempStr2)

        finalList = []
        for m in strpList:  # for each status response, split up the components
            finalList.append(m.split(','))

        for stat in finalList:  # establish each keyword=value pair
            if stat[0] == 'MRA':
                mra = stat[1]
                command.write(messageCode,
                              motorPositionA=f'(motorA={mra})')

            elif stat[0] == 'MRB':
                mrb = stat[1]
                command.write(messageCode,
                              motorPositionB=f'(motorB={mrb})')

            elif stat[0] == 'MRC':
                mrc = stat[1]
                command.write(messageCode,
                              motorPositionC=f'(motorC={mrc})')

            elif stat[0] == 'ENV':
                env0T = stat[2]
                env0H = stat[3]
                env1T = stat[4]
                env1H = stat[5]
                env2T = stat[6]
                env2H = stat[7]
                specMechT = stat[8]
                command.write(messageCode,
                              environments=f'(Temperature0={env0T}, Humidity0={env0H}, '
                                           f'Temperature1={env1T}, Humidity1={env1H}, '
                                           f'Temperature2={env2T}, Humidity2={env2H}, '
                                           f'SpecMechTemp={specMechT})')

            elif stat[0] == 'ACC':
                accx = stat[1]
                accy = stat[2]
                accz = stat[3]
                command.write(messageCode,
                              accelerometer=f'(xAxis={accx}, yAxis={accy}, zAxis={accz})')

            elif stat[0] == 'PNU':
                # change the c/o/t and 0/1 responses of specMech
                # to something more readable
                if stat[2] == 'c':
                    pnus = 'closed'
                elif stat[2] == 'o':
                    pnus = 'open'
                else:
                    pnus = 'transiting'

                if stat[4] == 'c':
                    pnul = 'closed'
                elif stat[4] == 'o':
                    pnul = 'open'
                else:
                    pnul = 'transiting'

                if stat[6] == 'c':
                    pnur = 'closed'
                elif stat[6] == 'o':
                    pnur = 'open'
                else:
                    pnur = 'transiting'

                if stat[8] == '0':
                    pnup = 'off'
                else:
                    pnup = 'on'

                command.write(messageCode,
                              pneumatics=f'(shutter={pnus}, leftHartmann={pnul}, '
                                         f'rightHartmann={pnur}, airPressure={pnup})')

            elif stat[0] == 'TIM':
                tim = stat[2]
                btm = stat[4]
                command.write(messageCode,
                              timeInfo=f'(bootTime={btm}, clockTime={tim})')

            elif stat[0] == 'VER':
                ver = stat[2]
                command.write(messageCode,
                              version=f'({ver})')

            elif stat[0] == 'VAC':
                red = stat[2]
                blue = stat[4]
                command.write(messageCode,
                              VacPumps=f'(redDewar={red}, blueDewar={blue})')

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
        self.reboot = False
        self.commandNumber = 0
        self.commandQueue = []

        # For the specMech emulator connection
        # self.ip = '127.0.0.1'
        # self.specMechPort = 8888

        # For the real specMech connection
        self.ip = 'specmech.mywire.org'
        self.specMechPort = 23

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
        loop.set_exception_handler(log.asyncio_exception_handler)

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
        # Parse the status response. Write a reply to the user for each relevant
        #  status string. This may be changed later.
        statusList = self.response.split("\r\x00\n")
        strpList = []

        for n in statusList:  # separate the individual status responses
            if '$S2' in n:
                tempStr1 = n[3:]  # remove '$S2'
                tempStr2 = tempStr1.split('*')[0]  # remove the NMEA checksum
                strpList.append(tempStr2)

        finalList = []
        for m in strpList:  # for each status response, split up the components
            finalList.append(m.split(','))

        # print(finalList)

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
        await actor_server()


if __name__ == "__main__":
    specActor = SpecActor()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('~~~Keyboard Interrupt~~~')
    except Exception as e:
        print(f'Unexpected Error: {e}')
