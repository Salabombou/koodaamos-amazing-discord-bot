from discord.ext import bridge
from utility.common import decorators
import discord

def command_check(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext):
    """
        Default checks for voice chat commands
    """
    if ctx.author.voice == None:
        return False  # if the user is not connected to a voice channel
    if ctx.me.voice == None:
        return True  # if the bot is currently not in a voice channel
    if ctx.author.voice.channel == ctx.me.voice.channel:
        return True  # if the bot and the user are in the same voice channel
    return False

@decorators.Async.logging.log
async def join(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> None | discord.VoiceClient:
    """
        Joins the same voice chat the user is in
    """
    if ctx.author.voice == None:
        return
    if ctx.me.voice == None:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        return vc
    
@decorators.Async.logging.log
async def leave(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> None:
    """
        Leaves the voice chat
    """
    if ctx.author.voice == None or ctx.me.voice == None:
        return
    if ctx.author.voice.channel != ctx.me.voice.channel:
        return
    if ctx.voice_client != None:
        await ctx.voice_client.disconnect()

@decorators.Sync.logging.log
def stop(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> None:
    """
        Stops the bot from playing audio
    """
    if ctx.voice_client == None or ctx.me.voice == None:
        return
    if ctx.author.voice == None or not ctx.voice_client.is_playing():
        return
    if ctx.author.voice.channel == ctx.me.voice.channel:
        ctx.voice_client.stop()

@decorators.Sync.logging.log
def resume(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> None:
    """
        Resumes the playing of audio
    """
    if ctx.voice_client == None or ctx.me.voice == None:
        return
    if ctx.author.voice == None or not ctx.voice_client.is_paused():
        return
    if ctx.author.voice.channel == ctx.me.voice.channel:
        ctx.voice_client.resume()

@decorators.Sync.logging.log
def pause(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> None:
    """
        Pauses the playing of audio
    """
    if ctx.voice_client == None or ctx.me.voice == None:
        return
    if ctx.author.voice == None or not ctx.voice_client.is_playing():
        return
    if ctx.author.voice.channel == ctx.me.voice.channel:
        ctx.guild.voice_client.pause()
