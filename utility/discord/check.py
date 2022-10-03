from discord.ext import commands

class command_checker:
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    async def check(self, ctx : commands.Context):
        if await self.bot.is_owner(ctx.author):
            ctx.command.reset_cooldown(ctx) # resets the cooldown of the command
            return True
        if ctx.author.bot:
            return False
        return True