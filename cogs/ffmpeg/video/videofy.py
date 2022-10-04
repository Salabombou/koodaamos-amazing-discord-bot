import io
from discord.ext import commands
from utility.discord import target as discordutil
from utility.common.command import respond
from utility.common import decorators, file_management
from utility.ffmpeg import *

class videofy(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'Adds audio to a image or a video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.img2vid_args = [
            '-loop', '1',
            '-ss', '00:00:00',
            '-to', '00:00:01',
            '-i', '"%s"',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-loglevel', 'error',
            '-shortest',
            '-movflags', 'frag_keyframe+empty_moov',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            'pipe:1'
        ]
        self.aud2vid_args = [
            
        ]

    async def create_output(self, ctx : commands.Context): 
        target = await discordutil.get_target(ctx, no_vid=True, no_aud=True)
        
        cmd = create_command(self.img2vid_args, target.proxy_url)
        out = await self.command_runner.run(cmd, arbitrary_command=True)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def vid(self, ctx : commands.Context):
        file, pomf_url = await self.create_output(ctx)
        await respond(ctx, content=pomf_url, file=file)