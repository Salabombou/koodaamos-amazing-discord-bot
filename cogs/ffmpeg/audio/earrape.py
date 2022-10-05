from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond

class earrape(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'yes'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.videofier = Videofier(bot.loop)
        self.earrape_args = [
            '-i', '-',
            '-af', 'acrusher=.1:1:64:0:log',
            ]

    async def create_output_video(self, ctx : commands.Context):
        target = await discordutil.get_target(ctx, no_img=True)

        stdin = await self.videofier.videofy(target)
        cmd = self.earrape_args
        out = await self.command_runner.run(cmd, stdin=stdin)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def er(self, ctx : commands.Context):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)