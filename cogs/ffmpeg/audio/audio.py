from discord.ext import commands
from utility.discord import target as discordutil
from utility.scraping import YouTube
from utility.common.command import respond
import httpx
from utility.common import decorators, file_management
from utility.ffmpeg import *

class audio(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'Adds audio to a image or a video'
        self.bot = bot
        self.command_runner = CommandRunner(bot.loop)
        self.client = httpx.AsyncClient(timeout=10)
        self.path_args = (
            'audio/target/',
            'audio/audio/audio/',
            'audio/audio/target/',
            'audio/audio/',
            'audio/output/'
            )
        self.target_audio_command = ['ffmpeg',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:d=1',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-map', '1:a?',
            '-vn',
            '-y',
            '-f', 'wav',
            '"%s"'
        ]
        self.merge_audio_command = ['ffmpeg',
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
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
            '-stream_loop', '-1',
            '-ss', '00:00:00',
            '-to', '%s',
            '-i', '"%s"',
            '-i', '"%s"',
            '-loglevel', 'error',
            '-t', '00:01:00',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-pix_fmt', 'yuv420p',
            '-f', 'mp4',
            '"%s"'
            ]
    async def create_output(self, ctx, url): 
        target = await discordutil.get_target(ctx, no_aud=True)
        audio = YouTube.get_info(url, video=False, max_duration=300)

        paths = create_paths(ctx.author.id, *self.path_args)
        (
            target_path,
            audio_audio_path,
            target_audio_path,
            audio_path,
            output_path,
        ) = paths

        inputs = [
            [target.proxy_url, target_path],
            [audio['url'], audio_audio_path]
            ]
        await save_files(inputs)

        time_to = create_time(audio['duration'])

        cmds = []
        cmds.append(create_command(self.target_audio_command, *(target_path, target_audio_path)))
        cmds.append(create_command(self.merge_audio_command, *(time_to, target_audio_path, audio_audio_path, audio_path)))
        cmds.append(create_command(self.merge_command, *(time_to, target_path, audio_path, output_path)))

        for cmd in cmds:
            await self.command_runner.run(cmd)

        pomf_url, file = await file_management.prepare_file(ctx, file=output_path, ext='mp4')
        return file, pomf_url
        
    @commands.command(help='url: a link to a YouTube video')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def audio(self, ctx, url="https://youtu.be/NOaSdO5H91M"):
        file, pomf_url = await self.create_output(ctx, url)
        await respond(ctx, content=pomf_url, file=file)