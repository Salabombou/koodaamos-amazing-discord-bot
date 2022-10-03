import io
from discord.ext import commands
from utility.discord import target as discordutil
from utility.scraping import YouTube
from utility.common.command import respond
from utility.common import decorators, file_management
from utility.ffmpeg import *
from PIL import Image

class videofy(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'Adds audio to a image or a video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.img2vid_args = [
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-f', 'image2pipe',
            #'-pixel_format', 'argb',
            #'-video_size', '%sx%s',
            '-framerate', '1',
            '-i', '-',
            #'-vf', '"pad=ceil(iw/2)*2:ceil(ih/2)*2"',
            '-map', '0:a',
            '-map', '1:v'
        ]
    
    async def pngfy(self, url):
        raw_img = await file_management.get_bytes(url)
        buf = io.BytesIO(raw_img)
        img = Image.open(buf)
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf.getvalue()

    async def create_output(self, ctx : commands.Context): 
        target = await discordutil.get_target(ctx, no_vid=True, no_aud=True)

        stdin = await self.pngfy(target.proxy_url)
        cmd = self.img2vid_args
        out = await self.command_runner.run(cmd, output='pipe:1', stdin=stdin)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def vid(self, ctx : commands.Context):
        file, pomf_url = await self.create_output(ctx)
        await respond(ctx, content=pomf_url, file=file)