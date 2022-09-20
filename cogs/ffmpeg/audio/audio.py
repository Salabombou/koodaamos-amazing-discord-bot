import asyncio
import time
from discord.ext import commands
import subprocess
from utility.discord import target as discordutil
from utility.scraping import YouTube, compress, pomf
from utility.common import decorators, file_management
from utility.common.errors import CommandTimeout, FfmpegError
from utility.common.command import respond
import os
import datetime
import functools
import httpx
import math

class audio(commands.Cog):
    def __init__(self, bot):
        self.description = 'Adds audio to a image or a video'
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=10)
        self.target_audio_command = ['ffmpeg',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-map', '1:a?',
            '-vn',
            '-y',
            '-f', 'wav',
            '"{}"'
        ]
        self.merge_audio_command = ['ffmpeg',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '{}',
            '-i', '"{}"',
            '-ss', '00:00:00',
            '-to', '00:00:30',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-filter_complex', '"[0][1]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]"',
            '-map', '"[a]"',
            '-ac', '1',
            '-y',
            '-f', 'wav',
            '"{}"'
            ]
        self.merge_command = ['ffmpeg',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '{}',
            '-i', '"{}"',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-vf', '"[0:v]scale={}:720"',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-y',
            '-f', 'mp4',
            '"{}"'
            ]
    async def create_output(self, ctx, url): 
        target = await discordutil.get_target(ctx, no_aud=True)
        audio = YouTube.get_info(url, video=False, max_duration=300)
        time_to = str(datetime.timedelta(seconds=audio['duration'] if audio['duration'] < 30 else 30))
        t_stamp = int(time.time())
        cwd = os.getcwd()
        width = math.ceil(((target.width / target.height) * 720) / 2) * 2

        target_path = cwd + f'/files/audio/target/{ctx.message.author.id}_{t_stamp}.mp4'
        audio_audio_path = cwd + f'/files/audio/audio/audio/{ctx.message.author.id}_{t_stamp}.wav'
        target_audio_path = cwd + f'/files/audio/audio/target/{ctx.message.author.id}_{t_stamp}.wav'
        audio_path = cwd + f'/files/audio/audio/{ctx.message.author.id}_{t_stamp}.wav'
        output_path = cwd + f'/files/audio/output/{ctx.message.author.id}_{t_stamp}.mp4'

        remove_args = (target_path, audio_audio_path, target_audio_path, audio_path, output_path)

        for input in [[target.proxy_url, target_path], [audio['url'], audio_audio_path]]:
            resp = await self.client.get(input[0])
            resp.raise_for_status()
            with open(input[1], 'wb') as file:
                file.write(resp.content)
                file.close()
        target_audio_cmd = ' '.join(self.target_audio_command).format(target_path, target_audio_path)
        merge_audio_cmd = ' '.join(self.merge_audio_command).format(time_to, target_audio_path, audio_audio_path, audio_path)
        merge_cmd = ' '.join(self.merge_command).format(time_to, target_path, audio_path, width, output_path)
        for cmd in [target_audio_cmd, merge_audio_cmd, merge_cmd]:
            try:
                pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE, timeout=60))
            except:
                asyncio.ensure_future(file_management.delete_temps(*remove_args))
                raise CommandTimeout()
            err = pipe.stderr.decode('utf-8') 
            if err != '':
                asyncio.ensure_future(file_management.delete_temps(*remove_args))
                raise FfmpegError(err)
        pomf_url, file = await file_management.prepare_file(ctx, file=output_path, ext='mp4')
        asyncio.ensure_future(file_management.delete_temps(*remove_args))
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def audio(self, ctx, url="https://youtu.be/NOaSdO5H91M"):
        file, pomf_url = await self.create_output(ctx, url)
        await respond(ctx, content=pomf_url, file=file)

def setup(client, tokens):
    client.add_cog(audio(client))