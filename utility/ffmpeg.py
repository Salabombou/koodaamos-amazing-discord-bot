from asyncio import AbstractEventLoop
from discord import Attachment, Embed, StickerItem
import os
import httpx
import math
import datetime
import time
import functools
import subprocess
from utility.common.errors import CommandTimeout, FfmpegError

client = httpx.AsyncClient()

def create_width(target : Attachment | Embed | StickerItem):
    width = math.ceil((target.width / target.height) * 720 / 2) * 2
    width = math.ceil(width / 2) * 2
    return width

def create_time(duration):
    return str(datetime.timedelta(seconds=duration))

def create_paths(ID, *args) -> tuple:
    timestamp = int(time.time())
    paths = []
    for arg in args:
        paths.append(f'./files/{arg}{ID}_{timestamp}.temp')
    return tuple(paths)

def create_command(command : list[str], *args):
    command = ' '.join(command) % args
    command = command.split(' ')
    return command

async def save_files(inputs) -> None:
    for input in inputs:
        resp = await client.get(input[0])
        resp.raise_for_status()
        with open(input[1], 'wb') as file:
            file.write(resp.content)
            file.close()

class CommandRunner:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    async def run(self, command : list, output: str = 'pipe:1', arbitrary_command=False, stdin=None) -> None:
        command = [
            'ffmpeg', *command
            ]
        if not arbitrary_command:
            command = [
               *command,
                '-loglevel', 'error',
                '-t', '00:01:00',
                '-movflags', 'frag_keyframe+empty_moov',
                '-pix_fmt', 'yuv420p',
                '-b:v', '200k',
                '-b:a', '96k',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-f', 'mp4',
                output
            ]
        try:
            if stdin == None:
                command = ' '.join(command)
            pipe = await self.loop.run_in_executor(
                None, functools.partial(
                    subprocess.run, command,
                    input=stdin,
                    bufsize=10**8,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60
                    )
                )
        except Exception as e:
            print(str(e))
            raise CommandTimeout()
        err = pipe.stderr.decode() 
        if err != '':
            raise FfmpegError(err)
        return pipe.stdout