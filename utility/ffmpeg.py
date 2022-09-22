import os
import httpx
import math
import datetime
import time
import functools
import subprocess
from utility.common.errors import CommandTimeout, FfmpegError

client = httpx.AsyncClient()

def create_width(target):
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

def create_command(command, *args):
    return ' '.join(command) % args

async def save_files(inputs) -> None:
    for input in inputs:
        resp = await client.get(input[0])
        resp.raise_for_status()
        with open(input[1], 'wb') as file:
            file.write(resp.content)
            file.close()

class CommandRunner:
    def __init__(self, loop) -> None:
        self.loop = loop
    async def run(self, command) -> None:
        try:
            pipe = await self.loop.run_in_executor(None, functools.partial(subprocess.run, command, stderr=subprocess.PIPE, timeout=60))
        except:
            raise CommandTimeout()
        err = pipe.stderr.decode('utf-8') 
        if err != '':
            raise FfmpegError(err)