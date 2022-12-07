import validators
from discord.ext import commands, bridge

from utility.cog.command import command_cog
from utility.common import decorators, file_management
from utility.common.command import respond
from utility.common.errors import UrlInvalid
from utility.common.requests import get_redirect_url
from utility.scraping import download as downl


class download(commands.Cog, command_cog):
    """
        Downloads a video, image or audio from multiple sources
        Supported sites:
            - Youtube
            - Reddit
            - TikTok
            - Spotify
        TBA:
            - Twitter
            - Twitch (clips)
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Downloads an video, image or audio from multiple sources'

    @bridge.bridge_command(help='url: a link to the downloadable content (YouTube, Reddit, Tiktok, Spotify)')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @bridge.guild_only()
    @decorators.Async.typing
    @decorators.Async.defer
    async def dl(self, ctx: bridge.BridgeExtContext, url):
        if not validators.url(url):
            raise UrlInvalid()
        url = await get_redirect_url(url)
        url, ext = await downl.from_url(url=url)
        resp = await self.client.get(url)
        resp.raise_for_status()
        pomf_url, file = await file_management.prepare_file(ctx, file=resp.content, ext=ext)
        await ctx.respond(pomf_url, file=file)