from discord.ext import commands, bridge
import discord

from utility.discord import target as discordutil
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.ffmpeg import *
from utility.cog.command import ffmpeg_cog


class bait(commands.Cog, ffmpeg_cog):
    """
        Creates a prank video that plays a YouTube video after the first frame of the video
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.ffprober = ffprobe.Ffprober(bot.loop)
        self.green_args = [
            '-to', '00:00:00.001',
            '-i', '-',
            '-i', '"%s"',
            '-filter_complex', '[0:v]select=not(mod(n\,1))[0v];[0v]scale={width}:{height},setsar=1[a];[1:v]scale={width}:{height},setsar=1[b];[a][0:a][b][1:a]concat=n=2:v=1:a=1[outv][outa]',
            '-map', '[outv]',
            '-map', '[outa]'
        ]

    async def create_output_video(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, url):
        # gets the target file
        target = await discordutil.get_target(ctx=ctx, no_aud=True)

        # gets the info from the youtube video specified
        video = await self.yt_extractor.get_info(url=url, video=True, max_duration=300)

        videofied = await self.videofier.videofy(target, duration=video['duration'], borderless=True)

        cmd = create_command(
            self.green_args,
            video['url'],
            width=videofied.width,
            height=videofied.height,
        )
        
        out = await self.command_runner.run(cmd, input=videofied.out, t=video['duration'] if video['duration'] < 60 else 60)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def bait(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        url: discord.Option(
            str,
            'A link to a YouTube video'
        ) = 'https://youtu.be/QCXmUplRd_M'
    ) -> None:
        """
            Create a prank video that plays a YouTube video after the first frame of the video
        """
        file, pomf_url = await self.create_output_video(ctx, url)
        await ctx.respond(pomf_url, file=file)
