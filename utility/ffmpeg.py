from asyncio import AbstractEventLoop
import math
import shlex
import httpx
import datetime
import functools
import subprocess
from utility.common.errors import FfmpegError
from utility.discord import target
import concurrent.futures
from utility import ffprobe
import tempfile

ideal_aspect_ratio = 16 / 9

min_width = 640
min_height = 360


def create_size(target: target.Target):
    width = target.width_safe
    height = target.height_safe

    if width == None or height == None:
        width = 1280
        height = 720
    elif width < min_width and height < min_height:
        width = min_width
        height = min_height

    aspect_ratio = width / height

    if aspect_ratio > ideal_aspect_ratio:
        height = round(width / ideal_aspect_ratio)
    elif aspect_ratio < ideal_aspect_ratio:
        width = round(height * ideal_aspect_ratio)

    width = math.ceil(width / 2) * 2
    height = math.ceil(height / 2) * 2

    return width, height


def create_time(duration):
    return str(datetime.timedelta(seconds=duration))


def create_command(command: list[str], *args, **kwargs):
    command: str = ' '.join(command) % args
    command = command.format(**kwargs)
    command = shlex.split(command, posix=False)
    return command


class CommandRunner:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop

    async def run(self, command: list, t: float = 60.0, output: str = 'pipe:1', arbitrary_command=False, input: bytes = None, max_duration: int | float = 60) -> None:
        output = output if output == 'pipe:1' else f'"{output}"'
        t = t if t < max_duration else max_duration
        command = [
            'ffmpeg',
            '-analyzeduration', '100M',
            '-probesize', '100M',
            *command,
            '-r', '30',
            '-t', f'{t}'
        ]
        if not arbitrary_command:
            command = [
                *command,
                '-loglevel', 'error',  # logs only errors
                '-pix_fmt', 'yuv420p',  # pixel format
                '-b:v', '1024k',  # video bitrate
                '-b:a', '128k',  # audio bitrate
                '-c:v', 'libx264',  # video codec
                '-movflags', 'frag_keyframe+empty_moov+faststart',  # 100% fragmented
                '-c:a', 'aac',  # audio codec
                '-crf', '28',  # level of compression
                '-preset', 'veryfast',
                '-ac', '1',  # mono sound
                '-y',  # overwrite file if exists without asking
                '-f', 'mp4',  # mp4 format
            ]
        command.append(output)
        command = ' '.join(command)
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pipe = await self.loop.run_in_executor(
                    pool, functools.partial(
                        subprocess.run, command,
                        input=input,
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

        return out if output == 'pipe:1' else output


class Videofied:
    def __init__(self, out: bytes, width, height) -> None:
        self.width = width
        self.height = height
        self.out = out


class Videofier:
    def __init__(self, loop: AbstractEventLoop):
        self.command_runner = CommandRunner(loop)
        self.prober = ffprobe.Ffprober(loop)
        self.to_video = [
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d={duration}',
            '-f', 'lavfi',
            '-i', 'color=c=0x36393e:s={width}x{height}:r=5:d={duration}',
            '-i', '"{path}"',
            '-vf', 'scale={scale},pad=ceil(iw/2)*2:ceil(ih/2)*2:color=0x36393e',
            '-map', '{map_video}:v:0',
            '-map', '{map_audio}:a'
        ]
        self.overlay_args = [
            '-f', 'lavfi',
            '-i', 'color=color=0x36393e@0.0:size={width}x{height},format=yuv420p',
            '-i', '-',
            '-filter_complex', '[0][1]overlay=(W-w)/2:(H-h)/2',
        ]
        self.loop_args = [
            '-stream_loop', '-1',
            '-ss', '00:00:00.1666666666666667',
            '-f', 'mp4',
            '-i', '"%s"',
        ]

    @staticmethod
    def get_scale(target: target.Target):
        min_safe_height = target.height_safe if target.height_safe >= min_height else min_height
        min_safe_width = target.width_safe if target.width_safe >= min_width else min_width

        ratio = target.width_safe / target.height_safe
        min_safe_ratio = min_safe_width / min_safe_height

        if ratio < min_safe_ratio:  # to make sure the ratio still stays the same
            min_safe_width = round(min_safe_height * ratio)
        elif ratio > min_safe_ratio:
            min_safe_height = round(min_safe_width / ratio)

        args = ('-2', min_safe_height) if min_safe_height > min_safe_width else (min_safe_width, '-2')

        scale = '%s:%s' % args
        return scale

    async def videofy(self, target: target.Target, duration: int | float = None, borderless: bool = False) -> Videofied:
        if duration is None:
            duration = target.duration_s
        with tempfile.TemporaryDirectory() as dir:  # create a temp dir, deletes itself and its content after use
            async with httpx.AsyncClient() as client:
                resp = await client.get(target.proxy_url)
                resp.raise_for_status()
                file = resp.content

            with tempfile.NamedTemporaryFile(delete=False, dir=dir) as temp:
                temp.write(file)
                temp.flush()
                kwargs = {
                    'width': target.width_safe,
                    'height': target.height_safe,
                    'scale': self.get_scale(target),
                    'path': temp.name,
                    'duration': target.duration_s,
                    'map_video': 1 if target.is_audio else 2,
                    'map_audio': 2 if target.has_audio else 0
                }
                cmd = create_command(self.to_video, **kwargs)
                out = await self.command_runner.run(cmd)

            # makes the width and height match 16/9 aspect ratio
            width, height = create_size(target)

            ratio = target.width_safe / target.height_safe
            if ratio > 4 or ratio < 0.25: # if the output would look wrong without borders
                borderless = False

            if not borderless:
                cmd = create_command(
                    self.overlay_args,
                    width=width,
                    height=height,
                    duration=target.duration_s
                )
                out = await self.command_runner.run(cmd, t=target.duration_s, input=out)

            # create a temp file in the temp dir
            with tempfile.NamedTemporaryFile(delete=False, dir=dir) as temp:
                temp.write(out)  # write into the temp file
                temp.flush()  # flush the file
                cmd = create_command(
                    self.loop_args,
                    temp.name  # path to the temp file
                )
                out = await self.command_runner.run(cmd, t=duration)

        return Videofied(out, width, height)
