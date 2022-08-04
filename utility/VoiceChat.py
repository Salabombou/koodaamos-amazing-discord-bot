def command_check(ctx):
    if ctx.author.bot: return False
    if ctx.author.voice == None: return False
    if ctx.me.voice == None: return True
    if ctx.author.voice.channel == ctx.me.voice.channel: return True
    
async def join(ctx):
    if ctx.message.author.voice == None:
        return
    if ctx.me.voice == None:
        channel = ctx.message.author.voice.channel
        await channel.connect()

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
        except: pass
        
async def resume(ctx):
    if ctx.message.author.voice == None or not ctx.voice_client.is_paused():
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        try:
            await ctx.voice_client.resume()
        except: pass

async def pause(ctx):
    if ctx.message.author.voice == None or not ctx.voice_client.is_playing():
        return
    if ctx.message.author.voice.channel == ctx.me.voice.channel and ctx.voice_client != None:
        try:
            await ctx.voice_client.pause()
        except: pass