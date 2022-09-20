from discord.ext import commands
import os
import discord
import httpx
from utility.discord import target as discordutil
from utility.scraping import YouTube
from utility.common import decorators, file_management
from utility.common.errors import CommandTimeout, FfmpegError
from utility.common.command import respond
import subprocess
import datetime
import urllib.parse
import time
import functools
import math
import asyncio
from utility.ffmpeg import *
class green(commands.Cog):
    def __init__(self, bot):
        self.description = 'Overlays a greenscreen video on top of an image / video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.client = httpx.AsyncClient(timeout=10)
        self.filter = '[2:v]scale=%s,fps=30,scale=-1:720,colorkey=0x%s:0.4:0[ckout];[1:v]fps=30,scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]'
        self.path_args = (
            'green/video/',
            'green/target/',
            'green/filtered/',
            'green/audio/video/',
            'green/audio/target/',
            'green/audio/',
            'green/output/'
            )
        self.ffmpeg_command = ['ffmpeg',
            '-ss', '00:00:00',
            '-to', '%s',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
            '-i', '"%s"',
            '-ss', '00:00:00',
            '-to', '00:00:30',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-filter_complex', self.filter % ('%s:720', '%s'),   #.format(scale='"%s"' + ':720', color='{color}'),
            '-map', '[out]',
            '-map', '0:a',
            '-y',
            '-f', 'mp4',
            '"%s"',
            '-map', '1:a?',
            '-vn',
            '-y',
            '-f', 'wav',
            '"%s"',
            '-map', '2:a',
            '-vn',
            '-y',
            '-f', 'wav',
            '%s'
            ]
        self.merge_audio_command = ['ffmpeg',
            '-i', '"%s"',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-filter_complex', '"[0][1]amerge=inputs=2,pan=stereo|FL<c0+c1|FR<c2+c3[a]"',
            '-map', '"[a]"',
            '-ac', '1',
            '-y',
            '-f', 'wav',
            '"%s"'
            ]
        self.merge_command = ['ffmpeg',
            '-ss', '00:00:00',
            '-to', '00:00:30',
            '-i', '"%s"',
            '-ss', '00:00:00',
            '-to', '00:00:30',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-y',
            '-f', 'mp4',
            '"%s"'
            ]

    def set_color(self, color):
        color = color.lower()
        color = color[:6].zfill(6)
        try: int(color, 16)
        except: color = '00ff00'
        return color

    async def create_output_video(self, ctx, url, color):
        target = await discordutil.get_target(ctx=ctx, no_aud=True)
        video = YouTube.get_info(url=url, video=True, max_duration=300)

        paths = create_paths(ctx.author.id, *self.path_args)
        (
            video_path,
            target_path,
            filtered_path,
            audio_video_path,
            audio_target_path,
            audio_path,
            output_path
        ) = paths

        inputs =  [
            [video['url'], video_path],
            [target.proxy_url, target_path]
            ]
        await save_files(inputs)

        width = create_width(target)
        time_to = create_time(video['duration'])
        color = self.set_color(color)

        cmds = []
        cmds.append(create_command(self.ffmpeg_command, *(time_to, time_to, target_path, video_path, width, color, filtered_path, audio_target_path, audio_video_path)))
        cmds.append(create_command(self.merge_audio_command, *(audio_target_path, audio_video_path, audio_path)))
        cmds.append(create_command(self.merge_command, *(filtered_path, audio_path, output_path)))

        for cmd in cmds:
            await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=output_path, ext='mp4')
        return file, pomf_url

    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def green(self, ctx, url='https://youtu.be/iUsecpG2bWI', color='00ff00'):
        file, pomf_url = await self.create_output_video(ctx, url, color)
        await respond(ctx, content=pomf_url, file=file)

def setup(client, tokens):
    client.add_cog(green(client))