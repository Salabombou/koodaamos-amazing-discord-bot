import os
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import CommandNotFound, CheckFailure
from help import help_command
from cogs import dalle, gpt3, tts, music, green, download, audio, nightcore, spam, eduko, sauce, earrape

def get_tokens():
    file = open(os.getcwd() + "/files/tokens", "r")
    return file.read().split("\n")

cogs = [dalle, gpt3, tts, music, green, download, audio, nightcore, spam, eduko, sauce, earrape]
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command=help_command())
tokens = get_tokens() # returns all the tokens

for cog in cogs:
    cog.setup(bot, tokens)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound): # ignores the error if it just didnt find the command
        return
    if isinstance(error, CheckFailure): # if the command didnt pass the check
        await ctx.message.add_reaction('👎')
        return
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{str(error)[0:4090]}```'
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/992830317733871636.gif')
    await ctx.reply(embed=embed)

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
            if member.bot == False:
                vc.resume()
                return
        vc.pause()
    elif vc in bot.voice_clients:
        for voice_client in bot.voice_clients:
            if voice_client.guild == vc.guild:
                for member in voice_client.channel.members:
                    if member.bot == False:
                        voice_client.resume()
                        return
                voice_client.pause()
                return

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('ready')

bot.run(tokens[0])