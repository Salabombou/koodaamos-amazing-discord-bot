import io
from discord.ext import commands
import urllib
import validators
from utility.common import decorators
from utility.scraping import compress, pomf
from utility.common.errors import UrlInvalid
import httpx
import discord

from utility.scraping import download as downl

class download(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'Downloads a video / image / audio from multiple sources'
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=10)

    @commands.command(help= 'url: a link to the downloadable content (YouTube, Reddit)')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def dl(self, ctx, url):
        if validators.url(url):
            resp = urllib.request.urlopen(url)
            url, ext = await downl.from_url(url=resp.url)
            resp = await self.client.get(url)
            resp.raise_for_status()
            file = await compress.video(resp.content, ctx)
            pomf_url = await pomf.upload(resp.content, ctx)
            if file != None:
                file = io.BytesIO(file)
                file = discord.File(fp=file, filename='unknown.' + ext)
            await ctx.reply(pomf_url, file=file)
        else: raise UrlInvalid()

def setup(client, tokens):
    client.add_cog(download(client, tokens))