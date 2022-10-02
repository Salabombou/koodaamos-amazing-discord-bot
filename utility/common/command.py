from discord.message import Message

async def respond(ctx, *args, **kwargs) -> Message:
    if not ctx.message:
        return await ctx.respond(*args, **kwargs)
    try:
        return await ctx.reply(*args, **kwargs)
    except:
        return await ctx.send(*args, **kwargs)