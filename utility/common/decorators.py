import asyncio
import functools

def get_server(ctx):
    return str(ctx.message.guild.id)

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
        await ctx.message.add_reaction('👌')
        return await func(*args, **kwargs)
    return wrapper
  
def delete_after(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        value = await func(*args, **kwargs)
        await asyncio.sleep(5)
        try:
            await ctx.message.delete()
        except: pass
        return value
    return wrapper