from discord.ext.commands import CommandNotFound, CommandInvokeError, CheckFailure
from discord import HTTPException, Forbidden, NotFound, ApplicationCommandInvokeError
import discord
from discord.ext import commands, bridge
from utility.common.command import respond
from utility.common.errors import NaughtyError
import os
import logging
import json
from urllib.parse import quote, quote_plus


with open('tokens.json') as file:
    tokens: dict = json.loads(file.read())

def _parse_text(text: str) -> str:
    for value in tokens.values():
        for value in [value, quote(value), quote_plus(value)]:
            text = text.replace(value, '<API_KEY>')
    return text

def create_error_embed(error):
    embed = discord.Embed(
        color=0xFF0000,
        fields=[],
        title='Something went wrong!'
    )
    error_text = _parse_text(str(error))
    embed.description = f'```{error_text[:4090]}```'
    embed.set_footer(
        icon_url='https://cdn.discordapp.com/emojis/992830317733871636.gif',
        text=type(error).__name__
    )
    return embed

class Listeners:
    """
        All the listeners to be added to the bot
    """
    def __init__(self, bot) -> None:
        self.bot = bot

    async def on_command_error(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, error):
        """
            When command raises an exception
        """
        if isinstance(error, CommandInvokeError):
            error = error.original  # gets the original exception from CommandInvokeError
        # ignores the error if it just didnt find the command
        if isinstance(error, CommandNotFound):
            return
        if isinstance(error, CheckFailure):
            await ctx.message.add_reaction('👎')
            return
        if isinstance(error, NaughtyError):
            return
        embed = create_error_embed(error)
        await ctx.respond(embed=embed)

    async def on_application_command_error(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, error):
        """
            When application command raises an exception
        """
        if isinstance(error, ApplicationCommandInvokeError):
            error = error.original  # gets the original exception from ApplicationCommandInvokeError
        if isinstance(error, NotFound):
            return
        if isinstance(error, CheckFailure):
            return
        if isinstance(error, NaughtyError):
            return
        embed = create_error_embed(error)
        await ctx.respond(embed=embed)

    async def on_ready(self):
        """
            Run once the bot is ready. Clears the terminal and prints 'ready'
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        print('ready')
