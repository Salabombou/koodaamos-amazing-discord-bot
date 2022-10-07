import json
from discord.ext import commands


class command_checker:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def naughty_list() -> list:
        with open('./naughty_list.json', 'r') as file:
            return list(json.loads(file.read()))

    async def check(self, ctx: commands.Context):
        if await self.bot.is_owner(ctx.author):
            # resets the cooldown of the command
            ctx.command.reset_cooldown(ctx)
            return True
        if ctx.author.id in self.naughty_list():
            return False
        if ctx.author.bot:
            return False
        return True
