import asyncio
import functools
import threading
import time
from discord.ext.commands import CommandNotFound, CommandInvokeError, CheckFailure
from discord import HTTPException, Forbidden, NotFound, ApplicationCommandInvokeError
import discord
from discord import ActivityType
from utility.common.command import respond
import os

def create_error_embed(error):
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{str(error)[:4090]}```'
    embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/992830317733871636.gif', text=type(error).__name__)
    return embed

def activity_updater(bot : discord.Bot):
    while True:
        for name in ['You', 'yOu', 'yoU', 'you']:
            time.sleep(1.5)
            asyncio.run(bot.change_presence(activity=discord.Activity(name=name, type=ActivityType.watching)))
        time.sleep(15)

class Listeners:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.x = threading.Thread(target=functools.partial(activity_updater, self.bot), name='activity_updater')

    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandInvokeError):
            error = error.original # gets the original exception from CommandInvokeError
        if isinstance(error, CommandNotFound): # ignores the error if it just didnt find the command
            return
        if isinstance(error, CheckFailure):
            return
        embed = create_error_embed(error)
        await respond(ctx, embed=embed)

    async def on_application_command_error(self, ctx, error):
        if isinstance(error, ApplicationCommandInvokeError):
            error = error.original # gets the original exception from ApplicationCommandInvokeError
        if isinstance(error, NotFound):
            return
        if isinstance(error, CheckFailure):
            return
        embed = create_error_embed(error)
        await ctx.send(embed=embed)
    

    async def on_error(self, event, ctx, error):
        if isinstance(error, CommandInvokeError):
            error = error.original # gets the original exception from CommandInvokeError
        if isinstance(error, HTTPException): # response could not be delivered
            return
        if isinstance(error, Forbidden): # bot does not have access to send a response
            return
        print(str(error))

    async def on_ready(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.x.start()
        print('ready')