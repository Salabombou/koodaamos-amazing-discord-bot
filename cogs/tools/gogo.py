from discord.ext import commands, bridge
import validators
import urllib.request
import urllib.parse
from utility.scraping import GogoAnime
from utility.common.errors import UrlInvalid
from utility.common import decorators
from utility.ui.views.gogo import anime_search_view

class gogo(commands.Cog):
    """
        *NOT IN USE*
        Gets the anime's stream url from GogoAnime
    """
    def __init__(self, bot, tokens):
        self.bot = bot

    @bridge.bridge_command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def gogo(self, ctx: bridge.BridgeContext, url=None):
        if url == None:
            await ctx.respond(view=anime_search_view())
            return
        if validators.url(url):
            try:
                m3u8_url = await GogoAnime.video_from_url(url)
            except:
                raise UrlInvalid()
            content = 'https://www.hlsplayer.org/play?url=' + urllib.parse.quote(m3u8_url)
            await ctx.respond(content)
        else:
            raise UrlInvalid()
