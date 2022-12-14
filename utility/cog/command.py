from discord.ext import commands
import httpx
from utility.ffmpeg import CommandRunner, Videofier
from utility.scraping.YouTube import YT_Extractor

class command_cog:
    """
        Default parent class is every cog
    """
    def __init__(self, bot: commands.Bot, tokens: dict, *args, **kwargs) -> None:
        self.bot = bot
        self.tokens = tokens
        self.client = httpx.AsyncClient()


class ffmpeg_cog:
    """
        Parent cog for ffmpeg commands
    """
    def __init__(self, bot: commands.Bot, tokens: dict, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.tokens = tokens
        self.command_runner = CommandRunner(bot.loop)
        self.videofier = Videofier(bot.loop)
        self.yt_extractor = YT_Extractor(bot.loop)