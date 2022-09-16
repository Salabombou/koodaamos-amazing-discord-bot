import asyncio
import functools

def get_server(ctx):
    return str(ctx.guild.id)

# shows the bot typing when running a command
def typing(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        async with ctx.typing():
            return await func(*args, **kwargs)
    return wrapper

    # adds a reaction to the message at the end
def add_reaction(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        if ctx.message != None:
            await ctx.message.add_reaction('👌')
        else:
            await ctx.respond('👌')
        return await func(*args, **kwargs)
    return wrapper
  
def delete_after(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        value = await func(*args, **kwargs)
        await asyncio.sleep(5)
        if ctx.message != None:
            await ctx.message.delete()
        else:
            await ctx.delete()
        return value
    return wrapper