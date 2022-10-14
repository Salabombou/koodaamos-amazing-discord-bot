from asyncio import AbstractEventLoop
import os
import httpx
import datetime
import functools
import subprocess
from utility.common.errors import FfmpegError
from utility.discord import target
import concurrent.futures
from utility import ffprobe
import tempfile

client = httpx.AsyncClient()

ideal_aspect_ratio = 16 / 9

def create_size(target: target.Target):
    width = target.width_safe
    height = target.height_safe

    if width == None or height == None:
        width = 1280
        height = 720

    aspect_ratio = width / height

    if aspect_ratio > ideal_aspect_ratio:
        height = round(width / ideal_aspect_ratio)
    elif aspect_ratio < ideal_aspect_ratio:
        width = round(height * ideal_aspect_ratio)

    return width, height


def create_time(duration):
    return str(datetime.timedelta(seconds=duration))


def create_command(command: list[str], *args, **kwargs):
    command: str = ' '.join(command) % args
    command = command.format(**kwargs)
    command = command.split(' ')
    return command


class CommandRunner:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    async def run(self, command: list, t: float = 60.0, output: str = 'pipe:1', arbitrary_command=False, stdin=None) -> None:
        command = [
            'ffmpeg',
            '-analyzeduration', '100M',
            '-probesize', '100M',
            *command,
            '-t', str(t)
        ]
        if not arbitrary_command:
            command = [
                *command,
                '-loglevel', 'error',  # logs only errors
                # '-movflags', 'frag_keyframe+empty_moov',  # 100% fragmented
                '-pix_fmt', 'yuv420p',  # pixel format
                '-b:v', '1024k',  # video bitrate
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
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pipe = await self.loop.run_in_executor(
                    pool, functools.partial(
                        subprocess.run, command,
                        input=stdin,
                        bufsize=8**10,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=60
                    )
                )
        except FfmpegError:
            raise FfmpegError('Command timeout')
        err: bytes = pipe.stderr
        out: bytes = pipe.stdout
        err = err.decode()
        if err != '':
            raise FfmpegError(err)

        return out


class Videofier:
    def __init__(self, loop: AbstractEventLoop):
        self.command_runner = CommandRunner(loop)
        self.prober = ffprobe.Ffprober(loop)
        self.to_video = [
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d={duration}',
            '-f', 'lavfi',
            '-i', 'color=c=0x36393e:s={width}x{width}:r=5:d={duration}',
            '-i', '"{url}"',
            '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2:color=0x36393e',
            '-map', '{map_video}:v:0',
            '-map', '{map_audio}:a'
        ]
        self.overlay_args = [
            '-f', 'lavfi',
            '-i', 'color=c=0x36393e:s={width}x{height}:r=30:d={duration}',
            '-i', '-',
            '-filter_complex', '"[0:v:0][1:v:0]overlay=(W-w)/2:(H-h)/2:enable=\'between(t,0,61)\'[out]"',
            '-map', '[out]',
            '-map', '1:a:0'
        ]
        self.loop_args = [
            '-stream_loop', '-1', # this breaks sometimes i have no idea why send help
            '-f', 'mp4',
            '-i', '"%s"',
        ]

    async def videofy(self, target: target.Target, duration: int | float = None) -> bytes:
        if duration is None:
            duration = target.duration_s

        kwargs = {
            'width': target.width_safe,
            'height': target.height_safe,
            'duration': target.duration_s,
            'url': target.proxy_url,
            'map_video': 1 if target.is_audio else 2,
            'map_audio': 2 if target.has_audio else 0
        }
        cmd = create_command(self.to_video, **kwargs)
        out = await self.command_runner.run(cmd)

        # makes the width and height match 16/9 aspect ratio
        width, height = create_size(target)

        # second run to add a gray 16/9 gray background and to fix any other issues
        cmd = create_command(
            self.overlay_args,
            width=width,
            height=height,
            duration=target.duration_s
        )
        out = await self.command_runner.run(cmd, t=target.duration_s, stdin=out)

        with tempfile.TemporaryDirectory() as dir: # create a temp dir, deletes itself and its content after use
            with tempfile.NamedTemporaryFile(delete=False, dir=dir) as tmp: # create a temp file in the temp dir
                tmp.write(out) # write into the temp file
                tmp.flush() # flush the file
                cmd = create_command(
                    self.loop_args,
                    tmp.name # path to the temp file
                )
                out = await self.command_runner.run(cmd, t=duration)

        return out
