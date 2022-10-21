import math
from discord.ext import commands
from utility.discord import target as discordutil
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.ffmpeg import *
from utility.cog.command import ffmpeg_cog


class bait(commands.Cog, ffmpeg_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Overlays a greenscreen video on top of an image or a video'
        self.ffprober = ffprobe.Ffprober(bot.loop)
        self.green_args = [
            '-to', '00:00:00.001',
            '-i', '-',
            '-i', '"%s"',
            '-filter_complex', '[0:v]select=not(mod(n\,1))[0v];[0v]scale={width}:{height},setsar=1[a];[1:v]scale={width}:{height},setsar=1[b];[a][0:a][b][1:a]concat=n=2:v=1:a=1[outv][outa]',
            '-map', '[outv]',
            '-map', '[outa]'
        ]

    async def create_output_video(self, ctx: commands.Context, url):
        # gets the target file
        target = await discordutil.get_target(ctx=ctx, no_aud=True)

        # gets the info from the youtube video specified
        video = await self.yt_extractor.get_info(url=url, video=True, max_duration=300)

        videofied = await self.videofier.videofy(target, duration=video['duration'])

        cmd = create_command(
            self.green_args,
            video['url'],
            width=videofied.width,
            height=videofied.height,
        )
        
        out = await self.command_runner.run(cmd, input=videofied.out, t=video['duration'] if video['duration'] < 60 else 60)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def bait(self, ctx: commands.Context, url='https://youtu.be/QCXmUplRd_M'):
        file, pomf_url = await self.create_output_video(ctx, url)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)
