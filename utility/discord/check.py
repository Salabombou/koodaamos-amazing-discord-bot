from discord import DMChannel
class command_checker:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def check(self, ctx):
        if ctx.author.bot:
            return False
        if isinstance(ctx.channel, DMChannel):
            return False
        return True