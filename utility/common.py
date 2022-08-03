import functools

# shows the bot typing when running a command
def typing(func):
    @functools.wraps(func)
    async def wrapper(*args):
        ctx = args[1]
        async with ctx.typing():
            return await func(*args)
    return wrapper