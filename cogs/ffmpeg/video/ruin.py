from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
import httpx

class ruin(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'yes'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)

        self.ruin_args= [
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-b:a', '10k',
            '-b:v', '10k',
            '-filter:v', 'fps=5',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-movflags', 'frag_keyframe+empty_moov',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            'pipe:1'
            ]

    async def create_output_video(self, ctx : commands.Context):
        target = await discordutil.get_target(ctx, no_img=True)

        cmd = create_command(self.ruin_args, target.proxy_url)
        out = await self.command_runner.run(cmd, arbitrary_command=True)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def ruin(self, ctx : commands.Context):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)