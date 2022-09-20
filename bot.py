from discord.ext.commands import CommandNotFound, CommandInvokeError, CheckFailure
from discord import HTTPException, Forbidden, NotFound, ApplicationCommandInvokeError
from utility.discord.help import help_command
from discord.ext import commands
import discord
import os
import json

from cogs.ffmpeg.audio import audio, nightcore, earrape
from cogs.ffmpeg.video import green
from cogs.fun import eduko
from cogs.fun.image import dalle, sauce
from cogs.fun.text import gpt3
from cogs.voice_chat import music
from cogs.tools import download

from utility.common.command import respond
from utility.common.file_management import TempRemover

def get_tokens():
    file = open('./tokens.json', 'r')
    return json.loads(file.read())

cogs = (dalle, gpt3, music, green, download, audio, nightcore, eduko, sauce, earrape)
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command=help_command())
tokens = get_tokens() # returns all the tokens

for cog in cogs:
    cog.setup(bot, tokens)

def create_error_embed(error):
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{str(error)[:4090]}```'
    embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/992830317733871636.gif', text=type(error).__name__)
    return embed

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandInvokeError):
        error = error.original
    if isinstance(error, CommandNotFound): # ignores the error if it just didnt find the command
        return
    if isinstance(error, CheckFailure):
        return
    embed = create_error_embed(error)
    await respond(ctx, embed=embed)

@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, ApplicationCommandInvokeError):
        error = error.original
    if isinstance(error, NotFound):
        return
    if isinstance(error, CheckFailure):
        return
    embed = create_error_embed(error)
    await ctx.send(embed=embed)
    
@bot.event
async def on_error(event, ctx, error):
    if isinstance(error, CommandInvokeError):
        error = error.original
    if isinstance(error, HTTPException):
        return
    if isinstance(error, Forbidden):
        return
    print(str(error))

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('ready')

TempRemover().start()

bot.run(tokens['discord'])