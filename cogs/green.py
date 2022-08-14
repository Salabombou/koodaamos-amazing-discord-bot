import io
import discord
from discord.ext import commands
import os
import discord
import httpx
from utility import discordutil, common, YouTube, compress
import subprocess
import datetime
import urllib.parse

class green(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filter = '"[1:v]scale=-1:720,colorkey=0x00ff00:0.4:0[ckout];[0:v]scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]"'
    
    async def create_output_video(self, ctx, url):
        video = YouTube.get_info(url=url, video=True)
        if video['duration'] > 60: raise Exception('Video is too long! Maximum duration is 60s.')
        time_to = str(datetime.timedelta(seconds=video['duration']))
        targeturl = await discordutil.GetFileUrl(ctx=ctx, no_aud=True)

        path = urllib.parse.urlparse(targeturl).path

        ext = os.path.splitext(path)[1]
        ext = '.png' if ext == '.jpg' or ext == '.jpeg' else ext # ffmpeg does not like jpgs

        video_path = f'{os.getcwd()}/files/green/video/{ctx.message.author.id}.mp4'
        resize_path = f'{os.getcwd()}/files/green/resize/{ctx.message.author.id}{ext}'
        output_path = f'{os.getcwd()}/files/green/output/{ctx.message.author.id}.mp4'
        
        resize_command = f'ffmpeg -i {targeturl} -s 1280x720 -vf setdar=16/9 -loglevel error -y ' + resize_path
        ffmpeg_command = f'ffmpeg -stream_loop -1 -ss 00:00:00 -to {time_to} -i "{resize_path}" -i "{video_path}" -loglevel error -filter_complex {self.filter} -map [out] -map 1:a? -y -f mp4 {output_path}'
        
        url = urllib.request.urlopen(video['url']).url # sometimes it redirects
        r = await httpx.AsyncClient().get(url)
        r.raise_for_status()
        with open(video_path, 'wb') as file:
            file.write(r.content)
            file.close()

        await ctx.bot.loop.run_in_executor(None, subprocess.Popen(resize_command).wait)
        await ctx.bot.loop.run_in_executor(None, subprocess.Popen(ffmpeg_command).wait)
        try:
            compressed = await compress.video(output_path)
            fp = io.BytesIO(compressed)
            return discord.File(fp=fp, filename='unknown.mp4'), [output_path, resize_path, video_path]
        except:
            raise Exception('Video creation failed')

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @common.decorators.typing
    async def green(self, ctx, url="https://youtu.be/iUsecpG2bWI"):
        if ctx.message.author.bot:
            return
        file, removable = await self.create_output_video(ctx, url)
        for temp in removable:
            os.remove(temp)
        await ctx.reply(file=file)

def setup(client, tokens):
    client.add_cog(green(client))