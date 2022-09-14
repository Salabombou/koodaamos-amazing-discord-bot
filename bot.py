from discord.ext.commands import CommandNotFound, CommandInvokeError, CheckFailure
from discord import HTTPException, Forbidden
from utility.discord.help import help_command
from discord.ext import commands
import discord
import asyncio
import os

from cogs.ffmpeg.audio import audio, nightcore, earrape
from cogs.ffmpeg.video import green
from cogs.fun import eduko, spam
from cogs.fun.image import dalle, sauce
from cogs.fun.text import gpt3
from cogs.voice_chat import music
from cogs.tools import download

def get_tokens():
    file = open(os.getcwd() + "/files/tokens", "r")
    return file.read().split("\n")

cogs = (dalle, gpt3, music, green, download, audio, nightcore, spam, eduko, sauce, earrape)
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command=help_command())
tokens = get_tokens() # returns all the tokens

for cog in cogs:
    cog.setup(bot, tokens)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound): # ignores the error if it just didnt find the command
        return
    if isinstance(error, CheckFailure):
        return
    if isinstance(error, CommandInvokeError):
        error = error.original
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{str(error)[:4090]}```'
    embed.set_footer(icon_url='https://cdn.discordapp.com/emojis/992830317733871636.gif', text=type(error).__name__)
    await ctx.reply(embed=embed)

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
async def on_voice_state_update(member, before, after):
    if after.channel == None: return
    vc = after.channel.guild.voice_client
    if before.channel is None and member.id == bot.user.id:
        time = 0
        condition = True
        while condition:
            await asyncio.sleep(1)
            time += 1
            if vc.is_playing() and not vc.is_paused():
                time = 0
            if time >= 1800:
                await vc.disconnect()
            condition = vc.is_connected()
    elif not member.id == bot.user.id and vc != None and bot.user in after.channel.members:
        for member in after.channel.members:
            if not member.bot:
                vc.resume()
                return
        vc.pause()
    elif vc in bot.voice_clients:
        for voice_client in bot.voice_clients:
            if voice_client.guild == vc.guild:
                for member in voice_client.channel.members:
                    if not member.bot:
                        voice_client.resume()
                        return
                voice_client.pause()
                return

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('ready')

bot.run(tokens[0])