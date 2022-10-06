from discord.ext import commands
from utility.discord import target as discordutil
from utility.ffmpeg import *
from utility.common import decorators, file_management
from utility.common.command import respond

class nightcore(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'makes the audio nightcore'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.videofier = Videofier(bot.loop)
        self.nightcore_args = [
            '-i', '-',
            '-filter_complex', '"[0:a]asetrate=1.25*44.1k,aresample=resampler=soxr:precision=24:osf=s32:tsf=s32p:osr=44.1k[a];[0:v]setpts=0.75*PTS[v]"',
            '-map', '[v]',
            '-map', '[a]',
            ]

    async def create_output_video(self,  ctx : commands.Context):
        target = await discordutil.get_target(ctx, no_img=True)
        await target.probe()

        stdin = await self.videofier.videofy(target)
        cmd = self.nightcore_args
        out = await self.command_runner.run(cmd, stdin=stdin)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def nc(self, ctx : commands.Context):
        file, pomf_url = await self.create_output_video(ctx)
        await respond(ctx, content=pomf_url, file=file, mention_author=False)