import asyncio
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
            return await func(*args)
        return wrapper
    
    def delete_after(func):
        @functools.wraps(func)
        async def wrapper(*args):
            ctx = args[1]
            value = await func(*args)
            await asyncio.sleep(5)
            try:
                await ctx.message.delete()
            except: pass
            return value
        return wrapper

def calculate_aspect(width: int, height: int) -> str:
    temp = 0

    def gcd(a, b):
        """The GCD (greatest common divisor) is the highest number that evenly divides both width and height."""
        return a if b == 0 else gcd(b, a % b)

    if width == height:
        return "1/1"

    if width < height:
        temp = width
        width = height
        height = temp

    divisor = gcd(width, height)

    x = int(width / divisor) if not temp else int(height / divisor)
    y = int(height / divisor) if not temp else int(width / divisor)

    return f"{x}/{y}"