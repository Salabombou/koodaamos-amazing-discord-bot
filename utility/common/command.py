from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Message

async def respond(ctx : commands.Context | ApplicationContext, *args, **kwargs) -> Message:
    if isinstance(ctx, ApplicationContext):
        return await ctx.respond(*args, **kwargs)
    try:
        return await ctx.reply(*args, **kwargs)
    except:
        return await ctx.send(*args, **kwargs)