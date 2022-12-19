from discord.ext import commands, bridge
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.cog.command import ffmpeg_cog


class nightcore(commands.Cog, ffmpeg_cog):
    """
        Makes video and its audio faster and more high pitched
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'makes the audio nightcore'
        self.nightcore_args = [
            '-i', '-',
            '-filter_complex', '"[0:a]asetrate=1.25*44.1k,aresample=resampler=soxr:precision=24:osf=s32:tsf=s32p:osr=44.1k[a];[0:v]setpts=0.75*PTS[v]"',
            '-map', '[v]',
            '-map', '[a]',
            '-shortest',
        ]

    async def create_output_video(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        target = await discordutil.get_target(ctx, no_img=True)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = self.nightcore_args
        out = await self.command_runner.run(cmd, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def nc(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        file, pomf_url = await self.create_output_video(ctx)
        await ctx.respond(pomf_url, file=file)
