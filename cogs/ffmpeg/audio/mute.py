from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.cog.command import ffmpeg_cog


class mute(commands.Cog, ffmpeg_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Mutes the audio of a video'
        self.mute_args = [
            '-i', '-',
            '-af', 'volume=0'
        ]

    async def create_output_video(self, ctx: commands.Context):
        target = await discordutil.get_target(ctx, no_img=True, no_aud=True)
        await target.probe()
        stdin = await self.videofier.videofy(target)
        cmd = self.mute_args
        out = await self.command_runner.run(cmd, stdin=stdin)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def mute(self, ctx: commands.Context):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)
