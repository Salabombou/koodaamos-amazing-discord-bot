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
        self.filter = '[2:v]scale={},fps=30,scale=-1:720,colorkey=0x00ff00:0.4:0[ckout];[1:v]fps=30,scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]'
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
            '-filter_complex', self.filter.format('"{width}"' + ':720'),
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
        filtered_path = cwd + f'/files/green/filtered/{ctx.message.author.id}_{t_stamp}.mp4'

        audio_video_path = cwd + f'/files/green/audio/video/{ctx.message.author.id}_{t_stamp}.wav'
        audio_target_path = cwd + f'/files/green/audio/target/{ctx.message.author.id}_{t_stamp}.wav'
        audio_path = cwd + f'/files/green/audio/{ctx.message.author.id}_{t_stamp}.wav'

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

        filter_cmd = ' '.join(self.ffmpeg_command).format(time_to=time_to, target=target_path, video=video_path, width=width, filtered=filtered_path, audio_target=audio_target_path, audio_video=audio_video_path)
        merge_audio_cmd = ' '.join(self.merge_audio_command).format(audio_target_path, audio_video_path, audio_path)
        merge_cmd = ' '.join(self.merge_command).format(filtered_path, audio_path, output_path)
        for cmd in [filter_cmd, merge_audio_cmd, merge_cmd]:
            pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE))
            err = pipe.stderr.decode('utf-8') 
            if err != '':
                raise Exception(err)
            
        compressed = await compress.video(output_path)
        fp = io.BytesIO(compressed)
        for temp in [video_path, target_path, filtered_path, audio_video_path, audio_target_path, audio_path, output_path]:
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