from discord.ext import commands
from utility.ffmpeg import CommandRunner, Videofier
import httpx
from utility.scraping.YouTube import YT_Extractor

class command_cog:
    def __init__(self, bot: commands.Bot, tokens: dict, *args, **kwargs) -> None:
        #super().__init__(**kwargs)
        self.bot = bot
        self.tokens = tokens
        self.client = httpx.AsyncClient()


class ffmpeg_cog:
    def __init__(self, bot: commands.Bot, tokens: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.tokens = tokens
        self.command_runner = CommandRunner(bot.loop)
        self.videofier = Videofier(bot.loop)
        self.yt_extractor = YT_Extractor(bot.loop)