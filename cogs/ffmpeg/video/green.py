from discord.ext import commands, bridge
import discord

from utility.discord.converter import Color
from utility.discord import target as discordutil
from utility.common import decorators, file_management
from utility.ffmpeg import *
from utility.cog.command import ffmpeg_cog


class green(commands.Cog, ffmpeg_cog):
    """
        Puts a greenscreen YouTube video on top of an image or a video
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.filter = '[1:v:0]scale=%s:%s,fps=30,colorkey=0x%s:0.4:0[ckout];[0:v:0]fps=30[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2[out]'
        self.green_args = [
            '-i', '-',
            '-i', '"%s"',
            '-filter_complex', self.filter % ('%s', '%s', '%s') + ';[0:a][1:a]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]',
            '-map', '[out]',
            '-map', '[a]'
        ]

    async def create_output_video(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        url: str,
        color: str
    ) -> tuple[str, str]:
        # gets the target file
        target = await discordutil.get_target(ctx=ctx, no_aud=True)

        # gets the info from the youtube video specified
        video = await self.yt_extractor.get_info(url=url, video=True, max_duration=300)

        width, height = create_size(target)

        videofied = await self.videofier.videofy(target, duration=video['duration'], borderless=True)

        cmd = create_command(
            self.green_args,
            video['url'],
            width,
            height,
            color
        )
        
        out = await self.command_runner.run(cmd, input=videofied.out, t=video['duration'] if video['duration'] < 60 else 60)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def green(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        url: bridge.core.BridgeOption(
            str,
            'A link to a YouTube video'
        ) = 'https://youtu.be/iUsecpG2bWI',
        color: bridge.core.BridgeOption(
            Color,
            'The color hex to filter the video with'
        ) = '00ff00'
    ) -> None:
        """
            Overlay a greenscreen video on top of an image or a video
        """
        file, pomf_url = await self.create_output_video(ctx, url, color)
        await ctx.respond(pomf_url, file=file)
