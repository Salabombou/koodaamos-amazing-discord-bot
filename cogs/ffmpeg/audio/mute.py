from discord.ext import commands, bridge
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.cog.command import ffmpeg_cog


class mute(commands.Cog, ffmpeg_cog):
    """
        Silences the targeted video
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Mutes the audio of a video'
        self.mute_args = [
            '-i', '-',
            '-af', 'volume=0'
        ]

    async def create_output_video(self, ctx: bridge.BridgeContext):
        target = await discordutil.get_target(ctx, no_img=True, no_aud=True)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = self.mute_args
        out = await self.command_runner.run(cmd, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def mute(self, ctx: bridge.BridgeContext):
        file, pomf_url = await self.create_output_video(ctx)
        await ctx.respond(pomf_url, file=file)
