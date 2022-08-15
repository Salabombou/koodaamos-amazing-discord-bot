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
import time
import functools

class green(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.filter = '[1:v]scale={},fps=30,scale=-1:720,colorkey=0x00ff00:0.4:0[ckout];[0:v]fps=30,scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]'
        self.ffmpeg_command = [
            f'ffmpeg',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '{}',
            '-i', '"{}"',
            '-i', '"{}"',
            '-filter_complex', self.filter.format('"{}"' + ':720'),
            '-loglevel', 'panic',
            '-map', '[out]',
            '-map', '1:a?',
            '-y',
            '-f', 'mp4',
            '"{}"'
            ]

    async def create_output_video(self, ctx, url):
        target = await discordutil.get_target(ctx=ctx, no_aud=True)
        width = int((target.width / target.height) * 720)
        video = YouTube.get_info(url=url, video=True)
        if video['duration'] > 60: raise Exception('Video is too long! Maximum duration is 60s.')
        time_to = str(datetime.timedelta(seconds=video['duration']))
        cwd = os.getcwd()
        t_stamp = int(time.time())
        video_path = cwd + f'/files/green/video/{ctx.message.author.id}_{t_stamp}.mp4'
        target_path = cwd + f'/files/green/target/{ctx.message.author.id}_{t_stamp}.mp4'
        output_path = cwd + f'/files/green/output/{ctx.message.author.id}_{t_stamp}.mp4'
        
        # because it will fuck up / be slow otherwise
        video_url = urllib.request.urlopen(video['url']).url # sometimes it redirects
        for i in [[video_url, video_path],[target.proxy_url, target_path]]:
            r = await httpx.AsyncClient(timeout=10).get(i[0])
            r.raise_for_status()
            with open(i[1], 'wb') as file:
                file.write(r.content)
                file.close()

        time_to = str(datetime.timedelta(seconds=video['duration']))
        width = int((target.width / target.height) * 720)
        cmd = ' '.join(self.ffmpeg_command).format(time_to, target_path, video_path, width, output_path)
        pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE))
        err = pipe.stderr.decode("utf-8") 
        if err != '':
            raise Exception(err)
        compressed = await compress.video(output_path)
        fp = io.BytesIO(compressed)
        for temp in [output_path, target_path, video_path]:
            os.remove(temp)
        return discord.File(fp=fp, filename='unknown.mp4')

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @common.decorators.typing
    async def green(self, ctx, url="https://youtu.be/iUsecpG2bWI"):
        if ctx.message.author.bot:
            return
        file = await self.create_output_video(ctx, url)
        await ctx.reply(file=file)

def setup(client, tokens):
    client.add_cog(green(client))