import discord

async def join(ctx):
    if ctx.message.author.voice == None:
        return
    channel = ctx.message.author.voice.channel
    if ctx.me.voice == None:
        await channel.connect()
    elif channel != ctx.me.voice.channel:
        await ctx.voice_client.move_to(channel)

async def leave(ctx):
    if ctx.message.author.voice == None:
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        await ctx.voice_client.disconnect()

async def stop(ctx):
    channel = ctx.message.author.voice.channel
    if ctx.message.author.voice == None or not ctx.voice_client.is_playing():
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        try:
            await ctx.voice_client.stop()
        except:
            pass
async def resume(ctx):
    if ctx.message.author.voice == None or not ctx.voice_client.is_paused():
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        try:
            await ctx.voice_client.resume()
        except:
            pass
async def pause(ctx):
    if ctx.message.author.voice == None or not ctx.voice_client.is_playing():
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        try:
            await ctx.voice_client.pause()
        except:
            pass