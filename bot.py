from utility.discord import help, check
from discord.ext import commands
from discord import Activity, ActivityType
import discord
import json

# imports all of the different event listeners
from utility.discord.listeners import Listeners

# imports all the used cogs
from cogs import *

# Setup the bot
bot = commands.Bot(
    command_prefix='.',
    intents=discord.Intents.all(),
    help_command=help.help_command(),
    activity=Activity(  # watching you
        name='you',
        type=ActivityType.watching
    )
)

# gets the tokens
with open('./tokens.json', 'r') as tokens_file:
    tokens = json.loads(tokens_file.read())

# cogs for the bot to use
cogs = (dalle, gpt3, music, green, ruin, download, audio,
        mute, nightcore, flanger, eduko, sauce, earrape, owner)
for cog in cogs:
    bot.add_cog(cog(bot, tokens))

# listeners for the bot to use
listener = Listeners(bot)
listeners = (listener.on_error, listener.on_application_command_error,
             listener.on_command_error, listener.on_ready)
for func in listeners:
    bot.add_listener(func=func)

bot.add_check(func=check.command_checker(bot).check)

if __name__ == '__main__':
    bot.run(tokens['discord'])
