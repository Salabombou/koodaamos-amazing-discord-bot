import os
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import CommandNotFound, CheckFailure

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
    if isinstance(error, CheckFailure): # if the command didnt pass the check
        await ctx.message.add_reaction('👎')
        return
    embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
    embed.description = f'```{error}```'[0:4096]
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/992830317733871636.gif')
    await ctx.reply(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and member.id == bot.user.id:
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time = time + 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 600:
                await voice.disconnect()
            if not voice.is_connected():
                break
    elif not member.id == bot.user.id:
        if before.channel != None:
            voice = before
        else:
            voice = after
        vc = voice.channel.guild.voice_client
        for member in voice.channel.members:
            if member.bot == False:
                try:
                    await vc.resume()
                except: pass # fuck you who ever made these to raise exception for no reason even when it works
                return
        try:
            await vc.pause()
        except: pass

@bot.event
async def on_ready():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('ready')

bot.run(tokens[0])