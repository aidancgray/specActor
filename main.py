#!/usr/bin/env python3
# specActor
# 12/18/2020
# Aidan Gray
# aidan.gray@idg.jhu.edu
#
# This is an actor for the BOSS specMech hardware microcontroller.

from specActor import SpecActor

from clu import command_parser
from contextlib import suppress
from sdsstools import get_logger
import asyncio
import click


NAME = 'sdss-boss-specActor'
log = get_logger(NAME)
log.start_file_logger('~/Desktop/specActor.log')


@command_parser.command()
async def test(command):
    """
    'test' command for testing out stuff
    """
    specActor.response = ''
    await specActor.send_data('wt9')

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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

    if '$S1ERR' in specActor.response:
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
@click.argument('STAT', type=click.Choice(['time', 'version', 'environment', 'vacuum',
                                           'motor-a', 'motor-b', 'motor-c',
                                           'orientation', 'pneumatics', '']),
                default='')
async def status(command, stat):
    """
    'status' command queries specMech for all status responses
    """
    if stat == 'time':
        dataTemp = 'rt'
    elif stat == 'version':
        dataTemp = 'rV'
    elif stat == 'environment':
        dataTemp = 're'
    elif stat == 'vacuum':
        dataTemp = 'rv'
    elif stat == 'motor-a':
        dataTemp = 'ra'
    elif stat == 'motor-b':
        dataTemp = 'rb'
    elif stat == 'motor-c':
        dataTemp = 'rc'
    elif stat == 'orientation':
        dataTemp = 'ro'
    elif stat == 'pneumatics':
        dataTemp = 'rp'
    else:
        dataTemp = 'rs'

    specActor.response = ''
    await specActor.send_data(dataTemp)

    if '$S1ERR' in specActor.response:
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
            if '$S1' in n:
                tempStr1 = n[3:]  # remove '$S1'
                tempStr2 = tempStr1.split('*')[0]  # remove the NMEA checksum
                strpList.append(tempStr2)

        finalList = []
        for m in strpList:  # for each status response, split up the components
            finalList.append(m.split(','))

        for stat in finalList:  # establish each keyword=value pair
            if stat[0] == 'MTR':
                mtr = stat[2]
                mtrPosition = stat[3]
                mtrPositionUnits = stat[4]
                mtrSpeed = stat[5]
                mtrSpeedUnits = stat[6]
                mtrCurrent = stat[7]
                mtrCurrentUnits = stat[8]
                command.write(messageCode,
                              motor=f'({mtr},{mtrPosition} {mtrPositionUnits},'
                                    f'{mtrSpeed} {mtrSpeedUnits},'
                                    f'{mtrCurrent} {mtrCurrentUnits})')

            elif stat[0] == 'ENV':
                env0T = stat[2] + ' ' + stat[3]
                env0H = stat[4] + ' ' + stat[5]
                env1T = stat[6] + ' ' + stat[7]
                env1H = stat[8] + ' ' + stat[9]
                env2T = stat[10] + ' ' + stat[11]
                env2H = stat[12] + ' ' + stat[13]
                specMechT = stat[14] + ' ' + stat[15]
                command.write(messageCode,
                              environments=f'(Temperature0={env0T}, Humidity0={env0H}, '
                                           f'Temperature1={env1T}, Humidity1={env1H}, '
                                           f'Temperature2={env2T}, Humidity2={env2H}, '
                                           f'SpecMechTemp={specMechT})')

            elif stat[0] == 'ORI':
                accx = stat[2]
                accy = stat[3]
                accz = stat[4]
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
                tim = stat[1]
                stim = stat[2]
                btm = stat[4]
                command.write(messageCode,
                              timeInfo=f'(bootTime={btm}, clockTime={tim}, setTime={stim})')

            elif stat[0] == 'VER':
                ver = stat[2]
                command.write(messageCode,
                              version=f'({ver})')

            elif stat[0] == 'VAC':
                red = stat[2]
                blue = stat[4]
                command.write(messageCode,
                              VacPumps=f'(redDewar={red}, blueDewar={blue})')

#         command.finish()


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
    specActor = SpecActor(log)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
    except Exception as e:
        print(f'Unexpected Error: {e}')
