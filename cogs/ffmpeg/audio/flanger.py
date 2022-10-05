from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond

class flanger(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'yes'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.flanger_args = [
            '-i', '"%s"',
            '-af', '"flanger=speed=%s:width=100"',
            ]
            
    async def create_output_video(self, ctx : commands.Context, speed):
        target = await discordutil.get_target(ctx, no_img=True)

        cmd = create_command(self.flanger_args, target.proxy_url, speed)
        out = await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def flan(self, ctx : commands.Context, speed=10.0):
        file, pomf_url = await self.create_output_video(ctx, speed)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)