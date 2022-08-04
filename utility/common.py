import functools

def get_server(ctx):
    return str(ctx.message.guild.id)

class decorators:
    # shows the bot typing when running a command
    def typing(func):
        @functools.wraps(func)
        async def wrapper(*args):
            ctx = args[1]
            async with ctx.typing():
                return await func(*args)
        return wrapper

    # adds a reaction to the message at the end
    def add_reaction(func):
        @functools.wraps(func)
        async def wrapper(*args):
            ctx = args[1]
            await ctx.message.add_reaction('👌')
            value = await func(*args)
            return value
        return wrapper