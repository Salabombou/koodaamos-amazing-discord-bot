import discord
from discord.ext import commands
import subprocess
from utility import discordutil
from utility import compress
from utility import YouTube
import os
import yt_dlp
import datetime
import ffmpeg
import asyncio

async def GetFile(ctx, imgurl, aud):    
    server = str(ctx.message.guild.id) + '\\'
    author = str(ctx.message.author.id) + '\\'
    outdir = os.getcwd() + '\\files\\audio\\output\\' + server + author
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outdir += "ou.mp4"
    ffmpegcmd = 'ffmpeg -i "' + imgurl + '" -i "' + aud['url'] + '" -s 1280x720 -vf "scale=\'bitand(oh*dar,65534)\':\'min(720,ih)\'" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -loglevel quiet -y ' + outdir
    vid_types = ['mp4', 'gif', 'mov', 'webm'] # accepted video types of discord
    to = str(datetime.timedelta(seconds=aud['duration']))
    imgtype = imgurl.split('.')[-1]
    if imgtype in vid_types: # if the image is not a stale image
        ffmpegcmd = 'ffmpeg -stream_loop -1 -ss 00:00:00 -to ' + to + ' -i "' + imgurl + '" -i "' + aud['url'] + '" -s 1280x720 -acodec copy -vcodec copy -map 0:v:0 -map 1:a:0 -loglevel quiet -y ' + outdir
    subprocess.Popen(ffmpegcmd).wait()
    compressed = await compress.Video(outdir, 8 * 1000)
    if compressed == False:
        return outdir
    os.remove(outdir)
    return compressed
        
class audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def audio(self,ctx,url="https://youtu.be/NOaSdO5H91M"): 
        # Program starts herer
        async with ctx.channel.typing():
            try:
                imgurl = await discordutil.GetFileUrl(ctx, no_aud=True)
                await ctx.send("Please wait, audio is being downloaded and converted...", delete_after=1)
                aud = await YouTube.ExtractInfo(url, audio=True)
                file = await GetFile(ctx, imgurl, aud)
                file = await GetFile(ctx, file, aud) # important for some fucking reason
                await ctx.reply(file=discord.File(file))
                os.remove(file)
                return
            except Exception as e:
                await ctx.reply("Something went wrong!\n```" + str(e) + "```", delete_after=3)
                await asyncio.sleep(3)
                await ctx.message.delete()
                print(str(e))
def setup(client, tokens):
    client.add_cog(audio(client))