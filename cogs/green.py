import discord
from discord.ext import commands
import os
import discord
import yt_dlp
from utility import discordutil
from utility import compress
from utility import YouTube
import asyncio
import subprocess
import datetime
import ffmpeg

filt = "[1:v]scale=-1:720,colorkey=0x00ff00:0.4:0[ckout];[0:v]scale=-1:720[ckout1];[ckout1][ckout]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2,pad=ceil(iw/2)*2:ceil(ih/2)*2[out]"

async def GetFile(imgurl, vidinfo, outdir, ctx): # converts to the green screen video and returns it as a discord.file
    opts = { # different things used in commands
        'img_type': imgurl.split('.')[-1],                               # type of file the image is
        'resize_img': outdir + 'resizeimg.' + imgurl.split('.')[-1],     # path of the resized image
        'resize_vid': outdir + 'resizevid.mp4',                          # path of the resized video
        'time_to': str(datetime.timedelta(seconds=vidinfo['duration'])), # duration of the greenscreen video
        'vid_url': vidinfo['url'],                                       # url of the video
        'vid_fps': str(vidinfo['fps'])                                   # fps of the video
    }
    outdir += 'out.mp4'
    
    resize_img_cmd = 'ffmpeg -i "' + imgurl + '" -s 1280x720 -vf setdar=16/9 -loglevel quiet -y ' + opts['resize_img']
    resize_vid_cmd = 'ffmpeg -i "' + opts['vid_url'] + '" -s 1280x720 -loglevel quiet -y ' + opts['resize_vid']
    output_vid_cmd = 'ffmpeg -i "' + opts['resize_img'] + '" -i "' + opts['resize_vid'] + '" -filter_complex ' + filt + " -map [out] -map 1:a? -loglevel quiet -y " + outdir

    vid_types = ['mp4', 'gif', 'mov', 'webm'] # accepted video types of discord
    if opts['img_type'] in vid_types: # if the image is not a stale image
        resize_img_cmd = 'ffmpeg -stream_loop -1 -ss 00:00:00 -to ' + opts['time_to'] + ' -i "' + imgurl + '" -s 1280x720 -vf setdar=16/9,fps=' + opts['vid_fps'] + ' -loglevel quiet -y ' + opts['resize_img']
    
    subprocess.Popen(resize_img_cmd).wait()
    subprocess.Popen(resize_vid_cmd).wait()
    subprocess.Popen(output_vid_cmd).wait()
    try:
        os.remove(opts['resize_img'])
        os.remove(opts['resize_vid'])
        compressed = await compress.Video(outdir, 8 * 1000)
        if compressed == False:
            return outdir
        os.remove(outdir)
        return compressed
    except:
        raise Exception("Could not create the video")

async def CreateOutputVideo(ctx, url):
    imgurl = await discordutil.GetFileUrl(ctx, no_aud=True)
    vidinfo = await YouTube.ExtractInfo(url)
    file = await GetFile(imgurl, vidinfo, outdir, ctx)
    return file



class green(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def green(self, ctx, url="https://youtu.be/YHPBO8OkYVo"):
        async with ctx.channel.typing():
            file = asyncio.create_task(CreateOutputVideo(ctx, url))
            await asyncio.Event().wait()
            await ctx.reply(file=discord.File(file))

def setup(client, tokens):
    client.add_cog(green(client))