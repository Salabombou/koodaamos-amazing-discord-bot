from discord.ext import commands
from utility.discord import target as discordutil
from utility.scraping import YouTube
from utility.common.command import respond
from utility.common import decorators, file_management
from utility.ffmpeg import *

class audio(commands.Cog):
    def __init__(self, bot : commands.Bot, tokens):
        self.description = 'Adds audio to a image or a video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.audio_args = [
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
            '-i', '"%s"',
            '-i', '"%s"',
            '-filter_complex', '"[%s:a:0][2:a:0]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a];[1:v]pad=ceil(iw/2)*2:ceil(ih/2)*2[v]"',
            '-map', '[a]',
            '-map', '[v]'
        ]
    
    async def create_output(self, ctx : commands.Context, url): 
        target = await discordutil.get_target(ctx, no_aud=True, no_img=True)
        audio = YouTube.get_info(url, video=False, max_duration=300)
        time_to = create_time(audio['duration'])


        cmd = create_command(self.audio_args, time_to, target.proxy_url, audio['url'], 0 if target.content_type == 'image' else 1)
        out = await self.command_runner.run(cmd, output='pipe:1')

        pomf_url, file = await file_management.prepare_file(ctx, file=out, ext='mp4')
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def audio(self, ctx : commands.Context, url="https://youtu.be/NOaSdO5H91M"):
        file, pomf_url = await self.create_output(ctx, url)
        await respond(ctx, content=pomf_url, file=file)