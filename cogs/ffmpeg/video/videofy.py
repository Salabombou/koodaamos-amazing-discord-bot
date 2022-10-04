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
            '-i', '"%s"',
            '-t', '1',
            '-vf', 'loop=-1:1',
            '-loglevel', 'error',
            '-movflags', 'frag_keyframe+empty_moov',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264',
            '-x264-params', 'lossless=1',
            '-movflags', 'frag_keyframe+empty_moov+faststart',
            '-f', 'mp4',
            'pipe:1'
        ]
        self.aud2vid_args = [
            '-f', 'lavfi',
            '-i', 'color=c=black:s=1280x720:r=5',
            '-i', '"%s"',
            '-t', '%s',
            '-loglevel', 'error',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', 'frag_keyframe+empty_moov+faststart',
            '-f', 'mp4',
            'pipe:1'
        ]

    async def create_output(self, ctx : commands.Context): 
        target = await discordutil.get_target(ctx, no_vid=True)
        if target.type == 'image':
            cmd = create_command(self.img2vid_args, target.proxy_url)
        elif target.type == 'audio':
            cmd = create_command(self.aud2vid_args, target.proxy_url, target.duration)
        out = await self.command_runner.run(cmd, arbitrary_command=True)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def videofy(self, ctx : commands.Context):
        file, pomf_url = await self.create_output(ctx)
        await respond(ctx, content=pomf_url, file=file)