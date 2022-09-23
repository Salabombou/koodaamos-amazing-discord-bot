from discord import DMChannel
class command_checker:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def check(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        if ctx.author.bot:
            return False
        return True