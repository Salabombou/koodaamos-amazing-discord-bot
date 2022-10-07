import asyncio
import functools
from discord.ext import commands
from discord.commands.context import ApplicationContext


def get_server(ctx: commands.Context):
    return str(ctx.guild.id)

# shows the bot typing when running a command


def typing(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
        async with ctx.typing():
            return await func(self, ctx, *args, **kwargs)
    return wrapper

    # adds a reaction to the message at the end


def add_reaction(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
        if isinstance(ctx, commands.Context):
            await ctx.message.add_reaction('👌')
        else:
            await ctx.respond('👌')
        return await func(self, ctx, *args, **kwargs)
    return wrapper


def delete_after(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
        value = await func(self, ctx, *args, **kwargs)
        await asyncio.sleep(5)
        if ctx.message != None:
            await ctx.message.delete()
        else:
            await ctx.delete()
        return value
    return wrapper
