def command_check(ctx):
    if ctx.author.bot:
        return False  # if the user is a bot
    if ctx.author.voice == None:
        return False # if the user is not connected to a voice channel
    if ctx.me.voice == None:
        return True # if the bot is currently not in a voice channel
    if ctx.author.voice.channel == ctx.me.voice.channel:
        return True # if the bot and the user are in the same voice channel
    
async def join(ctx):
    if ctx.message.author.voice == None: return
    if ctx.me.voice == None:
        channel = ctx.message.author.voice.channel
        await channel.connect()

async def leave(ctx):
    if ctx.message.author.voice == None or ctx.me.voice == None: return
    if ctx.message.author.voice.channel != ctx.me.voice.channel: return
    if ctx.voice_client != None:
        await ctx.voice_client.disconnect()

async def stop(ctx):
    if ctx.voice_client == None or ctx.me.voice == None: return
    if ctx.message.author.voice == None or not ctx.voice_client.is_playing(): return
    if ctx.message.author.voice.channel == ctx.me.voice.channel:
        ctx.voice_client.stop()

async def resume(ctx):
    if ctx.voice_client == None or ctx.me.voice == None: return
    if ctx.message.author.voice == None or not ctx.voice_client.is_paused(): return
    if ctx.message.author.voice.channel == ctx.me.voice.channel:
        ctx.voice_client.resume()

async def pause(ctx):
    if ctx.voice_client == None or ctx.me.voice == None: return
    if ctx.message.author.voice == None or not ctx.voice_client.is_playing(): return
    if ctx.message.author.voice.channel == ctx.me.voice.channel:
        ctx.guild.voice_client.pause()