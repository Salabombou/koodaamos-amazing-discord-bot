import os
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from cogs import dalle, gpt3, tts, music

def get_tokens():
    file = open(os.getcwd() + "/files/tokens", "r")
    return file.read().split("\n")

cogs = [dalle, gpt3, tts, music]
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
tokens = get_tokens() # returns all the tokens

for cog in cogs:
    cog.setup(bot, tokens)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound): # ignores the error if it just didnt find the command
        return
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{error}```'
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/992830317733871636.gif')
    await ctx.reply(embed=embed)

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('ready')

bot.run(tokens[0])