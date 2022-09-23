from discord.ext import commands
import urllib.request
import validators
from utility.common import decorators, file_management
from utility.common.errors import UrlInvalid
from utility.common.command import respond
import httpx

from utility.scraping import download as downl

class download(commands.Cog):
    def __init__(self, bot, tokens):
        self.description = 'Downloads a video / image / audio from multiple sources'
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=10)

    @commands.command(help= 'url: a link to the downloadable content (YouTube, Reddit)')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.typing
    async def dl(self, ctx, url):
        if validators.url(url):
            resp = urllib.request.urlopen(url)
            url, ext = await downl.from_url(url=resp.url)
            resp = await self.client.get(url)
            resp.raise_for_status()
            pomf_url, file = await file_management.prepare_file(ctx, file=resp.content, ext=ext)
            await respond(ctx, content=pomf_url, file=file)
        else: raise UrlInvalid()