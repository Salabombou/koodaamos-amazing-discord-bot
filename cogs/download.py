import io
from discord.ext import commands
import urllib
import validators
from utility.common import download as downl, decorators
from utility import compress
import httpx
import discord

class download(commands.Cog):
    def __init__(self, bot, tokens):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def dl(self, ctx, url):
        if validators.url(url):
            resp = urllib.request.urlopen(url)
            url, ext = await downl.from_url(url=resp.url)
            resp = await httpx.AsyncClient(timeout=10).get(url)
            resp.raise_for_status()
            file = resp.content
            file = await compress.video(file, ctx)
            file = io.BytesIO(file)
            file = discord.File(fp=file, filename='unknown.' + ext)
            await ctx.reply(file=file)
        else: raise Exception('Invalid url.')

def setup(client, tokens):
    client.add_cog(download(client, tokens))