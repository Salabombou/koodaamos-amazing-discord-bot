import io
import time
import discord
from discord.ext import commands
import subprocess
from utility import discordutil, compress, YouTube
from utility.common import file_management, decorators
import os
import yt_dlp
import datetime
import ffmpeg
import asyncio
import functools
import httpx
import math

class audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_audio_command = ['ffmpeg',
        '-f', 'lavfi',
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
        '-i', '"{}"',
        '-loglevel', 'error',
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
            '-i', '"{}"',
            '-loglevel', 'error',
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
            '-filter_complex', '"[0:v]scale={}:720"',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-y',
            '-f', 'mp4',
            '"{}"'
            ]
    async def create_output(self, ctx, url): 
        target = await discordutil.get_target(ctx, no_aud=True)
        audio = YouTube.get_info(url, video=False, max_duration=60)
        time_to = str(datetime.timedelta(seconds=audio['duration']))
        t_stamp = int(time.time())
        cwd = os.getcwd()
        width = int((target.width / target.height) * 720)
        width = math.ceil(width / 2) * 2

        target_path = cwd + f'/files/audio/target/{ctx.message.author.id}_{t_stamp}.mp4'
        audio_audio_path = cwd + f'/files/audio/audio/audio/{ctx.message.author.id}_{t_stamp}.wav'
        target_audio_path = cwd + f'/files/audio/audio/target/{ctx.message.author.id}_{t_stamp}.wav'
        audio_path = cwd + f'/files/audio/audio/{ctx.message.author.id}_{t_stamp}.wav'
        output_path = cwd + f'/files/audio/output/{ctx.message.author.id}_{t_stamp}.mp4'

        remove_args = (target_path, audio_audio_path, target_audio_path, audio_path, output_path)

        for i in [[target.proxy_url, target_path], [audio['url'], audio_audio_path]]:
            r = await httpx.AsyncClient(timeout=10).get(i[0])
            r.raise_for_status()
            with open(i[1], 'wb') as file:
                file.write(r.content)
                file.close()
        target_audio_cmd = ' '.join(self.target_audio_command).format(target_path, target_audio_path)
        merge_audio_cmd = ' '.join(self.merge_audio_command).format(time_to, target_audio_path, audio_audio_path, audio_path)
        merge_cmd = ' '.join(self.merge_command).format(time_to, target_path, audio_path, width, output_path)
        for cmd in [target_audio_cmd, merge_audio_cmd, merge_cmd]:
            try:
                pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE, timeout=15))
            except:
                file_management.delete_temps(*remove_args)
                raise Exception('Command timeout.')
            err = pipe.stderr.decode('utf-8') 
            if err != '':
                file_management.delete_temps(*remove_args)
                raise Exception(err)
        file = await compress.video(output_path, ctx)
        fp = io.BytesIO(file)
        file = discord.File(fp=fp, filename='unknown.mp4')
        file_management.delete_temps(*remove_args)
        return file
        
    @commands.command()
    @decorators.typing
    async def audio(self, ctx, url="https://youtu.be/NOaSdO5H91M"):
        file = await self.create_output(ctx, url)
        await ctx.reply(file=file)

def setup(client, tokens):
    client.add_cog(audio(client))