import asyncio
import discord
import functools
from discord.ext import commands
from discord.commands.context import ApplicationContext
import tempfile
from utility.logging import level, handler
import time
import logging


class Async:

    @staticmethod
    def typing(func):
        """
            Shows the bot typing when running a command
        """
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            async with ctx.typing():
                return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def add_reaction(func):
        """
            Adds a reaction to the message at the end
        """
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
        """
            Deletes the message five seconds after responding
        """
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
    
    class logging:
        
        @staticmethod
        def log(func):
            """
                Logs the function start and end
            """
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                func_name = func.__qualname__
                logger = logging.getLogger(func_name)
                logger.setLevel(level)
                logger.addHandler(handler)
                logger.info('starting')
                start = time.perf_counter()
                try:
                    value = await func(*args, **kwargs)
                except Exception as e:
                    logger.exception(f'ended with exception {type(e).__name__}')
                    raise e
                end = time.perf_counter()
                logger.info(f'ended with a time of {end-start:.2f} seconds')
                return value
            return wrapper
    
    class ffmpeg:
    
        @staticmethod
        def create_dir(func):
            """
                Creates a temporary directory for files in ffmpeg. Gets automatically deleted once the command has responded
            """
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                with tempfile.TemporaryDirectory() as dir:  # create a temp dir, deletes itself and its content after use
                    kwargs['_dir'] = dir
                    return await func(*args, **kwargs)
            return wrapper

    @staticmethod
    def update_playlist(func):
        """
            Updates the playlist in the music bot commands
        """
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
        """
            Gets the server id as str and passes it as a keyword arguement
        """
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context | ApplicationContext | discord.Message, *args, **kwargs):
            kwargs['server'] = str(ctx.guild.id)
            return await func(self, ctx, *args, **kwargs)
        return wrapper

class Sync: # synchronous versions for synchronous functions

    @staticmethod
    def update_playlist(func):
        """
            Updates the playlist in the music bot commands
        """
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
        """
            Gets the server id as str and passes it as a keyword arguement
        """
        @functools.wraps(func)
        def wrapper(self, ctx: commands.Context | ApplicationContext, *args, **kwargs):
            kwargs['server'] = str(ctx.guild.id)
            return func(self, ctx, *args, **kwargs)
        return wrapper
    
    class logging:
        
        @staticmethod
        def log(func):
            """
                Logs the function start and end
            """
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__qualname__
                logger = logging.getLogger(func_name)
                logger.setLevel(level)
                logger.addHandler(handler)
                logger.info('starting')
                start = time.perf_counter()
                try:
                    value = func(*args, **kwargs)
                except Exception as e:
                    logger.exception(f'ended with exception {type(e).__name__}')
                    raise e
                end = time.perf_counter()
                logger.info(f'ended with a time of {end-start:.2f} seconds')
                return value
            return wrapper