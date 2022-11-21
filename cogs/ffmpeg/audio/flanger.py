from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.cog.command import ffmpeg_cog


class flanger(commands.Cog, ffmpeg_cog):
    """
        Adds to video's audio or to an audio file a vibrato effect
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Adds a vibrato effect to audio'
        self.flanger_args = [
            '-i', '-',
            '-af', '"flanger=speed=%s:width=100"'
        ]

    async def create_output_video(self, ctx: commands.Context, speed):
        target = await discordutil.get_target(ctx, no_img=True)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = create_command(self.flanger_args, speed)
        out = await self.command_runner.run(cmd, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command(help='speed: the speed of the oscilation in Hz')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.Async.logging.log
    @decorators.Async.typing
    async def flan(self, ctx: commands.Context, speed=10.0):
        file, pomf_url = await self.create_output_video(ctx, speed)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)
