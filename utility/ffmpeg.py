from asyncio import AbstractEventLoop
from discord import Attachment, Embed, StickerItem
import httpx
import datetime
import time
import functools
import subprocess
from utility.common.errors import CommandTimeout, FfmpegError
from utility.discord import target

client = httpx.AsyncClient()

aspect_ratio = float(16/9)


def create_width(target: Attachment | Embed | StickerItem):
    width = round(target.height * aspect_ratio)
    return width


def create_time(duration):
    return str(datetime.timedelta(seconds=duration))


def create_paths(ID, *args) -> tuple:
    timestamp = int(time.time())
    paths = []
    for arg in args:
        paths.append(f'./files/{arg}{ID}_{timestamp}.temp')
    return tuple(paths)


def create_command(command: list[str], *args):
    command: str = ' '.join(command) % args
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

    async def run(self, command: list, t: float = 60.0, output: str = 'pipe:1', arbitrary_command=False, stdin=None) -> None:
        command = [
            'ffmpeg', *command,
            '-t', str(t)
        ]
        if not arbitrary_command:
            command = [
                *command,
                '-loglevel', 'error',  # logs only errors
                '-movflags', 'frag_keyframe+empty_moov',  # 100% fragmented
                '-pix_fmt', 'yuv420p',  # pixel format
                '-b:v', '256k',  # video bitrate
                '-b:a', '128k',  # audio bitrate
                '-c:v', 'libx264',  # video codec
                '-movflags', 'frag_keyframe+empty_moov+faststart',
                '-c:a', 'aac',  # audio codec
                '-crf', '28',
                '-preset', 'veryfast',
                '-ac', '1',  # mono sound
                '-f', 'mp4',  # mp4 format
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
        err: bytes = pipe.stderr
        out: bytes = pipe.stdout
        err = err.decode()
        if err != '':
            raise FfmpegError(err)
        return out


class Videofier:
    def __init__(self, loop: AbstractEventLoop):
        self.command_runner = CommandRunner(loop)
        self.img2vid_args = [
            '-analyzeduration', '100M',
            '-probesize', '100M',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=%sx%s:r=5',
            '-r', '5',
            '-i', '%s',
            '-loop', '-1:1',
            '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
        ]
        self.aud2vid_args = [
            '-analyzeduration', '100M',
            '-probesize', '100M',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=%sx%s:r=5',
            '-i', '%s',
        ]
        self.vid2vid_args = [
            '-analyzeduration', '100M',
            '-probesize', '100M',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=%sx%s:r=5',
            '-i', '%s',
            '-filter-complex', '"[1]split[m][a];[a]geq=\'if(gt(lum(X,Y),16),255,0)\',hue=s=0[al];[m][al]alphamerge[ovr]"',
            '-map', '[ovr]'
        ]

    async def videofy(self, target: target.Target) -> bytes:
        cmd = ''
        if target.type == 'video' or 'gifv':
            cmd = self.vid2vid_args
        if target.type == 'image':
            cmd = self.img2vid_args
        elif target.type == 'audio':
            cmd = self.aud2vid_args
        else:
            cmd = self.vid2vid_args
        if target.height == None:
            target.height = 720

        width = create_width(target)
        cmd = create_command(cmd, width, target.height, target.proxy_url)
        out = await self.command_runner.run(cmd, t=target.duration_s)

        # second run to fix any playback issues
        cmd = create_command(self.vid2vid_args, width, target.height, '-')
        out = await self.command_runner.run(cmd, t=target.duration_s, stdin=out)

        with open('debug.mp4', 'wb') as file:
            file.write(out)

        return out
