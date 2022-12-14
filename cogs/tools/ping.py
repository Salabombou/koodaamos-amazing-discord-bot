from discord.ext import commands, bridge
import time

from utility.cog.command import command_cog
from utility.common import decorators, command


class ping(commands.Cog, command_cog):
    """ 
        Test the response time of the bot
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.ping_results = lambda resp_time: f'Pong!\n```\nLatency: {self.bot.latency*1000:.2f}ms\nResponse time: {resp_time*1000:.2f}ms\n```'
        
    @bridge.bridge_command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @decorators.Async.defer
    async def ping(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Test the response time of the bot
        """
        start = time.perf_counter()
        message = await command.respond(ctx, 'Pong!')
        end = time.perf_counter()
        await message.edit(self.ping_results(end-start))