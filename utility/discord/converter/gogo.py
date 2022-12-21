from discord.ext import commands, bridge, pages

from utility.common.errors import UrlInvalid
from utility.scraping import GogoAnime


class GogoAnimeStreamUrl(commands.Converter):
    async def convert(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        url: str = None
    ) -> str:
        try:
            stream_url = await GogoAnime.video_from_url(url=url)
        except:
            raise UrlInvalid()
        return stream_url