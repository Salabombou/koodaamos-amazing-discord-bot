from discord.ext import commands, bridge
import validators
import urllib.request
import urllib.parse
from utility.scraping import GogoCdnExtractor
from utility.common.errors import UrlInvalid
from utility.common.command import respond
from utility.common import decorators


class gogo(commands.Cog):
    """
        *NOT IN USE*
        Gets the anime's stream url from GogoAnime
    """
    def __init__(self, bot, tokens):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.Async.typing
    async def gogo(self, ctx: commands.Context, url):
        if validators.url(url):
            try:
                m3u8_url = await GogoCdnExtractor.video_from_url(url)
            except:
                raise UrlInvalid()
            content = 'https://www.hlsplayer.org/play?url=' + \
                urllib.parse.quote(m3u8_url)
            await respond(ctx, content)
        else:
            raise UrlInvalid()
