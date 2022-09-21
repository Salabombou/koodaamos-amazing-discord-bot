from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.errors import CommandTimeout, FfmpegError
from utility.common.command import respond
import functools
import subprocess
import httpx
import asyncio

class nightcore(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'makes the audio of a video / audio nightcore'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.client = httpx.AsyncClient(timeout=10)
        self.path_args = (
            'nightcore/target/',
            'nightcore/audio/',
            'nightcore/output/'
            )
        self.ffmpeg_command = ['ffmpeg',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-filter_complex', '"[0:a:0]asetrate=1.25*44.1k,aresample=resampler=soxr:precision=24:osf=s32:tsf=s32p:osr=44.1k[out]"',
            '-map', '[out]',
            '-ac', '1',
            '-f', 'mp4',
            '"%s"'
            ]
        self.merge_command = ['ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=720x720:d=1',
            '-i', '"%s"',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-vf', '"[1:v?]setpts=PTS/1.25"',
            '-map', '1:v?',
            '-map', '0:v',
            '-map', '2:a:0',
            '-c:a', 'copy',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            '"%s"'
            ]
    async def create_output_video(self, ctx):
        target = await discordutil.get_target(ctx, no_img=True)

        paths = create_paths(ctx.author.id, *self.path_args)
        (
            target_path,
            audio_path,
            output_path,
        ) = paths

        inputs = [[target.proxy_url, target_path]]
        await save_files(inputs)

        cmds = []
        cmds.append(create_command(self.ffmpeg_command, *(target_path, audio_path)))
        cmds.append(create_command(self.merge_command, *(target_path, audio_path, output_path)))

        for cmd in cmds:
            await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=output_path, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def nc(self, ctx):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)