import json
from discord.ext import commands
import concurrent.futures
from utility.common.errors import NaughtyError


class command_checker:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def naughty_list() -> list:
        with open('naughty_list.json', 'r') as file:
            return list(json.loads(file.read()))
        
    async def get_naughty_list(self) -> list:
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await self.bot.loop.run_in_executor(
                pool, self.naughty_list
            )

    async def check(self, ctx: commands.Context):
        if await self.bot.is_owner(ctx.author): # owner's command is absolute
            # resets the cooldown of the command
            ctx.command.reset_cooldown(ctx)
            return True
        if ctx.author.id in await self.get_naughty_list():
            return False
        if ctx.author.bot:
            return False
        return True
