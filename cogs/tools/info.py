from discord.ext import commands, bridge
import discord
from utility.cog.command import command_cog
from utility.common import config


class info(commands.Cog, command_cog):
    """ 
        *WIP*
        Responds with embed with information about the bot's abilities
    """
    def __init__(self, bot: bridge.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.info_embed = discord.Embed(color=config.embed.color)        
    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        return await ctx.send(embed=self.info_embed)