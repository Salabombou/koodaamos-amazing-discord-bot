from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond

import httpx

class earrape(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'yes'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.client = httpx.AsyncClient(timeout=10)
        self.path_args = (
            'earrape/target/',
            'earrape/output/'
            )
        self.ffmpeg_command = ['ffmpeg',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-af', 'acrusher=.1:1:64:0:log',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            '"%s"'
            ]
    async def create_output_video(self, ctx):
        target = await discordutil.get_target(ctx, no_img=True)

        paths = create_paths(ctx.author.id, *self.path_args)
        (
            target_path,
            output_path
        ) = paths

        inputs = [[target.proxy_url, target_path]]
        await save_files(inputs)

        cmd = create_command(self.ffmpeg_command, *(target_path, output_path))
        await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=output_path, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def er(self, ctx):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)