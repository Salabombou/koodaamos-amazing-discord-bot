from discord.ext import commands, bridge
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.cog.command import ffmpeg_cog


class ruin(commands.Cog, ffmpeg_cog):
    """
        Ruins the video or audio completely by making its bitrate very small
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Ruins the quality of an image, video or audio'
        self.ruin_args = [
            '-i', '-',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-b:a', '10k',
            '-b:v', '50k',
            '-filter:v', 'fps=5',
            '-loglevel', 'error',
            '-t', '60',
            '-movflags', 'frag_keyframe+empty_moov',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
        ]

    async def create_output_video(self, ctx: bridge.BridgeExtContext):
        target = await discordutil.get_target(ctx)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = self.ruin_args
        out = await self.command_runner.run(cmd, arbitrary_command=True, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def ruin(self, ctx: bridge.BridgeExtContext):
        file, pomf_url = await self.create_output_video(ctx)
        await ctx.respond(pomf_url, file=file)
