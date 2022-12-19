from discord.ext import commands, bridge

from utility.discord import target as discordutil
from utility.common import decorators, file_management
from utility.ffmpeg import *
from utility.cog.command import ffmpeg_cog


class text(commands.Cog, ffmpeg_cog):
    """
        Adds top text to an image or video
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.text_args = [
            '-i', '-',
            '-filter_complex', '"[0]pad=width=iw:height=(ih+(ih/5)):x=0:y=(ih/5):color=white[padded];[padded]drawtext=fontfile=\'C\:/Windows/Fonts/arial.ttf\':fontsize={fontsize}:text=\'%s\':x=(w-text_w)/2:y=(h-text_h)/15[out]"',
            '-map', '[out]',
            '-map', '0:a'
        ]

    async def create_output_video(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        text: str
    ) -> None:
        target = await discordutil.get_target(ctx)

        videofied = await self.videofier.videofy(target, borderless=True)

        cmd = create_command(self.text_args, text, fontsize=videofied.width / len(text))
        out = await self.command_runner.run(cmd, input=videofied.out)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def text(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        text: bridge.core.BridgeOption(
            str,
            'The text to add to the video or image'
        )
    ) -> None:
        """
            Add top text to an image or video
        """
        file, pomf_url = await self.create_output_video(ctx, text)
        await ctx.respond(pomf_url, file=file)
