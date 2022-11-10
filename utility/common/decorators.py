import asyncio
import functools
from discord.ext import commands
from discord.commands.context import ApplicationContext


class Async:

    @staticmethod
    def typing(func):  # shows the bot typing when running a command
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            async with ctx.typing():
                return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def add_reaction(func):  # adds a reaction to the message at the end
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            if isinstance(ctx, commands.Context):
                await ctx.message.add_reaction('👌')
            else:
                await ctx.respond('👌')
            return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
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

    @staticmethod
    def update_playlist(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            server = str(ctx.guild.id)
            if not server in self.tools.playlist:
                self.tools.playlist[server] = [[], []]
            if server not in self.tools.looping:
                self.tools.looping[server] = False
            return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def get_server(func):  # passes the server id as a string since its needed to access some dicts
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            kwargs['server'] = str(ctx.guild.id)
            return await func(self, ctx, *args, **kwargs)
        return wrapper

class Sync: # synchronous versions for synchronous functions

    @staticmethod
    def update_playlist(func):
        @functools.wraps(func)
        def wrapper(self, ctx: commands.Context, *args, **kwargs):
            server = str(ctx.guild.id)
            if not server in self.tools.playlist:
                self.tools.playlist[server] = [[], []]
            if server not in self.tools.looping:
                self.tools.looping[server] = False
            return func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def get_server(func):  # passes the server id as a string since its needed to access some dicts
        @functools.wraps(func)
        def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            kwargs['server'] = str(ctx.guild.id)
            return func(self, ctx, *args, **kwargs)
        return wrapper
