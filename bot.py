from utility.discord import help, check
from discord.ext import commands
import discord
import json

# imports all of the different event listeners
from utility.discord.listeners import Listeners

# imports the onwer commands only the bot owner can run
from utility.discord.owner import owner_cog

# imports all the used cogs
from cogs.ffmpeg.audio.audio import audio
from cogs.ffmpeg.audio.earrape import earrape
from cogs.ffmpeg.audio.nightcore import nightcore
from cogs.ffmpeg.audio.flanger import flanger
from cogs.ffmpeg.video.green import green
from cogs.fun.eduko import eduko
from cogs.fun.image.dalle import dalle
from cogs.fun.image.sauce import sauce
from cogs.fun.text.gpt3 import gpt3
from cogs.voice_chat.music import music
from cogs.tools.download import download

from utility.common.file_management import TempRemover

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command=help.help_command(), activity=discord.Activity(name='you', type=discord.ActivityType.watching))

# gets the tokens
with open('./tokens.json', 'r') as tokens_file:
    tokens = json.loads(tokens_file.read())  

# cogs for the bot to use
cogs = (dalle, gpt3, music, green, download, audio, nightcore, flanger, eduko, sauce, earrape, owner_cog) 
for cog in cogs:
    bot.add_cog(cog(bot, tokens))

# listeners for the bot to use
listener = Listeners(bot)
listeners = (listener.on_error, listener.on_application_command_error, listener.on_command_error, listener.on_ready)
for func in listeners:
    bot.add_listener(func=func)

bot.add_check(func=check.command_checker(bot).check)

# starts the temp remover that deletes temp files after they reach 5 mins in age
TempRemover().start()

bot.run(tokens['discord'])