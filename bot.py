from utility.discord import help, check
from discord.ext import commands
from discord import Activity, ActivityType
import discord
import json

# imports all of the different event listeners
from utility.discord.listeners import Listeners

# imports all the used cogs
from cogs import *

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Setup the bot
bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all(),
    help_command=help.help_command(),
    activity=Activity(  # watching you
        type=ActivityType.watching,
        name='you'
    )
)

# gets the tokens
with open('tokens.json') as file:
    tokens = json.loads(file.read())

# cogs for the bot to use
cogs = (
    dalle, gpt3,
    music, green,
    ruin, download,
    audio, mute,
    nightcore, flanger,
    eduko, sauce,
    earrape, owner,
    bait
    #removebg
)
for cog in cogs:
    bot.add_cog(cog(bot, tokens))

# listeners for the bot to use
listener = Listeners(bot)
listeners = (
    listener.on_error,
    listener.on_application_command_error,
    listener.on_command_error,
    listener.on_ready
)
for func in listeners:
    bot.add_listener(func=func)

bot.add_check(func=check.command_checker(bot).check)

if __name__ == '__main__':
    bot.run(tokens['discord'])
