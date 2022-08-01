import os
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, CommandOnCooldown, NSFWChannelRequired
from discord.errors import NotFound

#from modules import spam
#from modules import eduko
#from modules import green
#from modules import sauce
#from modules import audio
#from modules import pixiv
#from modules import dalle
#from modules import gpt3
#from modules import tts
#from modules import moist
from modules import music
# the token variable are as such:
# 0: discord bot token
# 1: gpt3 token

def GetTokens():
    file = open("./files/tokens", "r")
    return file.read().split("\n")

cogs = [music] #[dalle] + [gpt3] + [tts] + [music] #[moist] + [music]# + [eduko]# + [green] #[eduko] + [green] + [sauce] + [audio]
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())

tokens = GetTokens()
for i in range(len(cogs)):
    cogs[i].setup(bot, tokens)

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
    os.system("clear")
    print("ready")

bot.run(tokens[0]) # throws exception 'NoneType' object has no attribute 'sequence' sometimes while i try to debug on my laptop send help