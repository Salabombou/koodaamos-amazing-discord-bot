from discord.ext import commands, bridge
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.cog.command import ffmpeg_cog


class earrape(commands.Cog, ffmpeg_cog):
    """
        Ruins the audio in the video and makes it very loud
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Makes the audio earrape'
        self.earrape_args = [
            '-i', '-',
            '-af', 'acrusher=.1:1:64:0:log',
        ]

    async def create_output_video(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        target = await discordutil.get_target(ctx, no_img=True)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = self.earrape_args
        out = await self.command_runner.run(cmd, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def er(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Ruin the audio of a video by making it extremely loud
        """
        file, pomf_url = await self.create_output_video(ctx)
        await ctx.respond(content=pomf_url, file=file)
