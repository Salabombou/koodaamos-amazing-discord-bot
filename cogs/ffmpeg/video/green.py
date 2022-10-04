from discord.ext import commands
from utility.discord import target as discordutil
from utility.scraping import YouTube
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.ffmpeg import *
from utility.ffprobe import Ffprober

class green(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'Overlays a greenscreen video on top of an image / video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop) # class used to run ffmpeg commands
        self.filter = '[2:v]scale=%s,fps=30,scale=-1:720,colorkey=0x%s:0.4:0[ckout];[1:v]fps=30,scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]'
        self.green_args = [
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
            '-i', '"%s"',
            '-i', '"%s"',
            '-filter_complex', self.filter % ('%s:720', '%s') + ';[%s:a][2:a]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]',
            '-map', '[out]',
            '-map', '[a]',
            ]

    def set_color(self, color : str): # sets the color for ffmpeg to filter
        color = color.lower()
        color = color[:6].zfill(6) # fills with zeros if missing values
        try: int(color, 16)
        except: color = '000ff00' # green if it fails to be converted to hexadecimal
        return color

    async def create_output_video(self, ctx : commands.Context, url, color):
        target = await discordutil.get_target(ctx=ctx, no_aud=True, no_img=True) # gets the target file

        video = YouTube.get_info(url=url, video=True, max_duration=300) # gets the info from the youtube video specified

        width = create_width(target) # creates a width that is divisible by two
        time_to = create_time(video['duration']) # creates the duration in format hh:mm:ss
        color = self.set_color(color) # creates the color

        cmd = create_command(self.green_args, time_to, time_to, target.proxy_url, video['url'], width, color )
        out = await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url

    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def green(self, ctx : commands.Context, url='https://youtu.be/iUsecpG2bWI', color='00ff00'):
        file, pomf_url = await self.create_output_video(ctx, url, color)
        await respond(ctx, content=pomf_url, file=file)