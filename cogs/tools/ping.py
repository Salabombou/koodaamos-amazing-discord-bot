from discord.ext import commands
from utility.cog.command import command_cog
import time


class ping(commands.Cog, command_cog):
    """ 
        Test the response speed of the bot
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.ping_results = lambda resp_time: f'Pong!\n```\nLatency: {self.bot.latency*1000:.2f}ms\nResponse time: {resp_time*1000:.2f}ms\n```'
        
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        start = time.perf_counter()
        message = await ctx.send(f'Pong!')
        end = time.perf_counter()
        await message.edit(self.ping_results(end-start))