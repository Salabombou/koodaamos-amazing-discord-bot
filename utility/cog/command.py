from discord.ext import commands
from utility.ffmpeg import CommandRunner, Videofier
import httpx


class command_cog:
    def __init__(self, bot : commands.Bot, tokens : dict) -> None:
        self.bot = bot
        self.tokens = tokens
        self.client = httpx.AsyncClient()

class ffmpeg_cog:
    def __init__(self, bot : commands.Bot, tokens : dict) -> None:
        self.bot = bot
        self.tokens = tokens
        self.command_runner = CommandRunner(bot.loop)
        self.videofier = Videofier(bot.loop)