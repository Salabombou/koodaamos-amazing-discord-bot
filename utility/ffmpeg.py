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
from utility.common import file_management
from discord.ext import commands
from utility.discord import target

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

    async def run(self, command : list, t=60, output: str = 'pipe:1', arbitrary_command=False, stdin=None) -> None:
        command = [
            'ffmpeg', *command,
            '-t', str(t)
            ]
        if not arbitrary_command:
            command = [
               *command,
                '-loglevel', 'error', # logs only errors
                '-movflags', 'frag_keyframe+empty_moov', # 100% fragmented
                '-pix_fmt', 'yuv420p', # pixel format
                '-b:v', '256k', # video bitrate
                '-b:a', '128k', # audio bitrate
                '-c:v', 'libx264', # video codec
                '-x264-params', 'lossless=1', # lossless quality
                '-movflags', 'frag_keyframe+empty_moov+faststart',
                '-c:a', 'aac', # audio codec
                '-crf', '27',
                '-preset', 'veryfast',
                '-ac', '1', # mono sound
                '-f', 'mp4', # mp4 format
            ]
        command.append(output)
        try:
            command = ' '.join(command)
            pipe = await self.loop.run_in_executor(
                None, functools.partial(
                    subprocess.run, command,
                    input=stdin,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=180
                    )
                )
        except:
            raise CommandTimeout()
        err = pipe.stderr.decode() 
        if pipe.stdout == b'':
            raise FfmpegError(err)
        return pipe.stdout

class Videofier:
    def __init__(self, loop : AbstractEventLoop):
        self.description = 'Adds audio to a image or a video'
        self.command_runner = CommandRunner(loop)
        self.img2vid_args = [
            '-framerate', '5',
            '-i', '"%s"',
            '-t', '%s',
            '-vf', 'loop=-1:1'
        ]
        self.aud2vid_args = [
            '-f', 'lavfi',
            '-i', 'color=c=black:s=1280x720:r=5',
            '-i', '"%s"',
            '-t', '%s'
        ]
        self.vid2vid_args = [
            '-i', '"%s"',
            '-t', '%s'            
        ]
    async def videofy(self, target : target.Target) -> bytes: 
        cmd = ''
        if target.type == 'video':
            cmd = self.vid2vid_args
        if target.type == 'image':
            cmd = self.img2vid_args
        elif target.type == 'audio':
            cmd = self.aud2vid_args

        cmd = create_command(
            cmd,
            target.proxy_url,
            target.duration if target.type == 'audio' else 1
            )
        out = await self.command_runner.run(cmd)

        return out