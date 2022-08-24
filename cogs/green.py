import io
import discord
from discord.ext import commands
import os
import discord
import httpx
from utility import discordutil, YouTube, compress
from utility.common import decorators, file_management
import subprocess
import datetime
import urllib.parse
import time
import functools
import math

class green(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=10)
        self.filter = '[2:v]scale={scale},fps=30,scale=-1:720,colorkey=0x{color}:0.4:0[ckout];[1:v]fps=30,scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]'
        self.ffmpeg_command = ['ffmpeg',
            '-ss', '00:00:00',
            '-to', '{time_to}',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '{time_to}',
            '-i', '"{target}"',
            '-i', '"{video}"',
            '-loglevel', 'error',
            '-filter_complex', self.filter.format(scale='"{width}"' + ':720', color='{color}'),
            '-map', '[out]',
            '-map', '0:a',
            '-y',
            '-f', 'mp4',
            '"{filtered}"',
            '-map', '1:a?',
            '-vn',
            '-y',
            '"{audio_target}"',
            '-map', '2:a',
            '-vn',
            '-y',
            '{audio_video}'
            ]
        self.merge_audio_command = ['ffmpeg',
            '-i', '"{}"',
            '-i', '"{}"',
            '-filter_complex', '"[0][1]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]"',
            '-loglevel', 'error',
            '-map', '"[a]"',
            '-ac', '1',
            '-y',
            '"{}"'
            ]
        self.merge_command = ['ffmpeg',
            '-i', '"{}"',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-c:v', 'copy',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-y',
            '"{}"'
            ]

    def set_color(self, color):
        color = color.lower()
        color = color[:6].zfill(6)
        try: int(color, 16)
        except: color = '00ff00'
        return color

    async def create_output_video(self, ctx, url, color):
        target = await discordutil.get_target(ctx=ctx, no_aud=True)
        width = math.ceil((target.width / target.height) * 720 / 2) * 2
        width = math.ceil(width / 2) * 2
        video = YouTube.get_info(url=url, video=True, max_duration=100)
        time_to = str(datetime.timedelta(seconds=video['duration']))

        cwd = os.getcwd()
        t_stamp = int(time.time())

        video_path = cwd + f'/files/green/video/{ctx.message.author.id}_{t_stamp}.mp4'
        target_path = cwd + f'/files/green/target/{ctx.message.author.id}_{t_stamp}.mp4'
        filtered_path = cwd + f'/files/green/filtered/{ctx.message.author.id}_{t_stamp}.mp4'

        audio_video_path = cwd + f'/files/green/audio/video/{ctx.message.author.id}_{t_stamp}.wav'
        audio_target_path = cwd + f'/files/green/audio/target/{ctx.message.author.id}_{t_stamp}.wav'
        audio_path = cwd + f'/files/green/audio/{ctx.message.author.id}_{t_stamp}.wav'

        output_path = cwd + f'/files/green/output/{ctx.message.author.id}_{t_stamp}.mp4'

        remove_args = (video_path, target_path, filtered_path, audio_video_path, audio_target_path, audio_path, output_path)

        # because it will fuck up / be slow otherwise
        video_url = urllib.request.urlopen(video['url']).url # sometimes it redirects
        for i in [[video_url, video_path],[target.proxy_url, target_path]]:
            r = await self.client.get(i[0])
            r.raise_for_status()
            with open(i[1], 'wb') as file:
                file.write(r.content)
                file.close()

        time_to = str(datetime.timedelta(seconds=video['duration']))
        width = int((target.width / target.height) * 720)
        color = self.set_color(color)
        filter_cmd = ' '.join(self.ffmpeg_command).format(time_to=time_to, target=target_path, video=video_path, width=width, color=color, filtered=filtered_path, audio_target=audio_target_path, audio_video=audio_video_path)
        merge_audio_cmd = ' '.join(self.merge_audio_command).format(audio_target_path, audio_video_path, audio_path)
        merge_cmd = ' '.join(self.merge_command).format(filtered_path, audio_path, output_path)
        for cmd in [filter_cmd, merge_audio_cmd, merge_cmd]:
            try:
                pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE, timeout=60))
            except:
                file_management.delete_temps(*remove_args)
                raise Exception('Command timeout.')
            err = pipe.stderr.decode('utf-8') 
            if err != '':
                file_management.delete_temps(*remove_args)
                raise Exception(err)
            
        compressed = await compress.video(output_path, ctx)
        file_management.delete_temps(*remove_args)
        fp = io.BytesIO(compressed)
        return discord.File(fp=fp, filename='unknown.mp4')

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def green(self, ctx, url='https://youtu.be/iUsecpG2bWI', color='00ff00'):
        if ctx.message.author.bot:
            return
        file = await self.create_output_video(ctx, url, color)
        await ctx.reply(file=file)

def setup(client, tokens):
    client.add_cog(green(client))