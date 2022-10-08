from asyncio import AbstractEventLoop
import httpx
import datetime
import functools
import subprocess
from utility.common.errors import CommandTimeout, FfmpegError
from utility.discord import target

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
                #'-movflags', 'frag_keyframe+empty_moov',  # 100% fragmented
                '-pix_fmt', 'yuv420p',  # pixel format
                '-b:v', '512k',  # video bitrate
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
                    bufsize=10**8,
                    timeout=180
                )
            )
        except:
            print('ffmpeg')
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
            '-r', '30',
            '-i', '{input}',
            '-loop', '-1:1',
            '-filter_complex', '[0:v]scale={width}:{height}[out]',
            '-map', '[out]',
            '-map', '0:a',
        ]
        self.aud2vid_args = [
            '-f', 'lavfi',
            '-i', 'color=c=black:s={width}x{height}:r=5',
            '-i', '{input}',
            '-map', '1:v',
            '-map', '1:a'
        ]
        self.vid2vid_args = [
            '-i', '{input}',
            '-filter_complex', '[0:v]scale={width}:{height},framerate=30[out]',
            '-map', '[out]',
            '-map', '0:a'
        ]
        self.overlay_args = [
            '-f', 'lavfi',
            '-i', 'color=c=0x36393e:s={width}x{height}:r=30:d={duration}',
            '-i', '-',
            '-filter_complex', '"[0:v][1:v]overlay=(W-w)/2:(H-h)/2:enable=\'between(t,0,20)\'[out]"',
            '-map', '[out]',
            '-map', '1:a'
        ]

    def get_cmd(self, target: target.Target):
        cmd = ''

        if target.width_safe == None or target.height_safe == None:
            target.width_safe = 1280
            target.height_safe = 720

        if target.type == 'image' or target.type == 'rich':
            cmd = self.img2vid_args
        elif target.type == 'video' or target.type == 'gifv':
            cmd = self.vid2vid_args
        elif target.type == 'audio':
            cmd = self.aud2vid_args

        cmd = create_command(
            cmd,
            input='-',
            width=target.width_safe,
            height=target.height_safe
        )

        return cmd

    async def videofy(self, target: target.Target) -> bytes:
        out = await self.command_runner.run(
            [
                '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:d={target.duration_s}',
                '-i', target.proxy_url,
                '-map', '1:v',
                '-map', f'{1 if target.has_audio else 0}:a'
            ]
        )

        cmd = self.get_cmd(target)
        out = await self.command_runner.run(cmd, t=target.duration_s, stdin=out)
        
        width, height = create_size(target)

        # second run to fix any playback issues
        cmd = create_command(self.overlay_args, width=width, height=height, duration=target.duration_s)
        out = await self.command_runner.run(cmd, t=target.duration_s, stdin=out)

        with open ('debug.mp4', 'wb') as file:
            file.write(out)
        return out
