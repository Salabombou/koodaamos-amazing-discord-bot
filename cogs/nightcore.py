import time
from discord.ext import commands
from utility import discordutil
from utility.common import file_management, decorators
from utility import compress
import io
import discord
import functools
import subprocess
import os
import httpx
class nightcore(commands.Cog):
    def __init__(self, bot, tokens):
        self.bot = bot
        self.ffmpeg_command = ['ffmpeg',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-filter_complex', '"[0:a:0]asetrate=1.15*44.1k,aresample=resampler=soxr:precision=24:osf=s32:tsf=s32p:osr=44.1k[out]"',
            '-map', '[out]',
            '-ac', '1',
            '"{}"'
            ]
        self.merge_command = ['ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=c=black:s=720x720:d=1',
            '-i', '"{}"',
            '-i', '"{}"',
            '-loglevel', 'error',
            '-vf', '[1:v?]setpts=PTS/1.15',
            '-map', '1:v?',
            '-map', '0:v',
            '-map', '2:a:0',
            '-f', 'mp4',
            '"{}"'
            ]
    async def create_output_video(self, ctx):
        target = await discordutil.get_target(ctx, no_img=True)
        cwd = os.getcwd()
        t_stamp = int(time.time())
        target_path = cwd + f'/files/nightcore/target/{ctx.message.author.id}_{t_stamp}.mp4'
        audio_path = cwd + f'/files/nightcore/audio/{ctx.message.author.id}_{t_stamp}.mp3'
        output_path = cwd + f'/files/nightcore/output/{ctx.message.author.id}_{t_stamp}.mp3'
        remove_args = (target_path, audio_path, output_path)
        r = await httpx.AsyncClient(timeout=10).get(target.proxy_url)
        r.raise_for_status()
        with open(target_path, 'wb') as file:
            file.write(r.content)
            file.close()
        ffmpeg_cmd = ' '.join(self.ffmpeg_command).format(target_path, audio_path)
        merge_cmd = ' '.join(self.merge_command).format(target_path, audio_path, output_path)
        for cmd in [ffmpeg_cmd, merge_cmd]:
            try:
                pipe = await ctx.bot.loop.run_in_executor(None, functools.partial(subprocess.run, cmd, stderr=subprocess.PIPE, timeout=15))
            except:
                file_management.delete_temps(*remove_args)
                raise Exception('Command timeout.')
            err = pipe.stderr.decode('utf-8') 
            if err != '':
                file_management.delete_temps(*remove_args)
                raise Exception(err)
        file = await compress.video(output_path, ctx)
        fp = io.BytesIO(file)
        file = discord.File(fp=fp, filename='unknown.mp4')
        file_management.delete_temps(*remove_args)
        return file

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def nc(self, ctx):
        if ctx.message.author.bot:
            return
        file = await self.create_output_video(ctx)
        await ctx.reply(file=file, mention_author=False)

def setup(client, tokens):
    client.add_cog(nightcore(client, tokens))