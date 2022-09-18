import time
from discord.ext import commands
from utility.discord import target as discordutil
from utility.scraping import compress, pomf
from utility.common import decorators, file_management
from utility.common.errors import CommandTimeout, FfmpegError
from utility.common.command import respond
import io
import discord
import functools
import subprocess
import os
import httpx
import asyncio

class earrape(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'makes the audio of a video / audio nightcore'
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=10)
        self.ffmpeg_command = ['ffmpeg',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-af', 'acrusher=.1:1:64:0:log',
            '"{}"'
            ]
    async def create_output_video(self, ctx):
        target = await discordutil.get_target(ctx, no_img=True)

        cwd = os.getcwd()
        t_stamp = int(time.time())

        target_path = cwd + f'/files/earrape/target/{ctx.message.author.id}_{t_stamp}.mp4'
        output_path = cwd + f'/files/earrape/output/{ctx.message.author.id}_{t_stamp}.mp4'
        remove_args = (target_path, output_path)

        r = await self.client.get(target.proxy_url)
        r.raise_for_status()
        with open(target_path, 'wb') as file:
            file.write(r.content)
            file.close()
        ffmpeg_cmd = ' '.join(self.ffmpeg_command).format(target_path, output_path)
        try:
            pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, ffmpeg_cmd, stderr=subprocess.PIPE, timeout=60))
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

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def er(self, ctx):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)

def setup(client, tokens):
    client.add_cog(earrape(client, tokens))