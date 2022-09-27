import asyncio
from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond

import httpx

class ruin(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'yes'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.client = httpx.AsyncClient(timeout=10)

        self.ffmpeg_params = [
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-b:a', '10k',
            '-b:v', '10k',
            '-filter:v', 'fps=5',
            ]

    async def create_output_video(self, ctx):
        target = await discordutil.get_target(ctx, no_img=True)

        cmd = create_command(self.ffmpeg_params, target.proxy_url)
        out = await self.command_runner.run(cmd, output='pipe:1')

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def ruin(self, ctx):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)