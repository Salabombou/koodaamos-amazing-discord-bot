from discord.ext import commands, bridge

from utility.discord import target as discordutil
from utility.common import decorators, file_management, command
from utility.ffmpeg import *
from utility.cog.command import ffmpeg_cog

class audio(commands.Cog, ffmpeg_cog):
    """
        Add audio from YouTube video on top of an image or video
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.audio_args = [
            '-i', '-',
            '-i', '"%s"',
            '-filter_complex', '"[0:a][1:a]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]"',
            '-map', '0:v:0',
            '-map', '[a]',
        ]

    async def create_output(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, url):
        target = await discordutil.get_target(ctx)

        audio = await self.yt_extractor.get_info(url, video=False, max_duration=300)

        cmd = create_command(
            self.audio_args,
            audio['url'],
        )

        videofied = await self.videofier.videofy(target, duration=audio['duration'], borderless=True)
        out = await self.command_runner.run(cmd, input=videofied.out, t=audio['duration'])

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def audio(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        url: bridge.core.BridgeOption(
            str,
            'A link to a YouTube video'
        ) = 'https://youtu.be/NOaSdO5H91M'
    ) -> None:
        """
            Add audio from YouTube video on top of an image or video
        """
        file, pomf_url = await self.create_output(ctx, url)
        await command.respond(ctx, pomf_url, file=file)
