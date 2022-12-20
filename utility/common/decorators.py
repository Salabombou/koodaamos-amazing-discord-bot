import asyncio
import discord
import functools
from discord.ext import commands, bridge
from discord.ext.bridge import BridgeApplicationContext, BridgeExtContext, BridgeContext
from discord.commands.context import ApplicationContext
import tempfile
from utility.logging import level, handler
import time
import logging
import inspect

class Async:

    @staticmethod
    def typing(func):
        """
            Shows the bot typing when running a command
        """
        @functools.wraps(func)
        async def wrapper(self, ctx: BridgeApplicationContext | BridgeExtContext, *args, **kwargs):
            if isinstance(ctx, BridgeApplicationContext):
                return await func(self, ctx, *args, **kwargs)
            async with ctx.typing():
                return await func(self, ctx, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def defer(func):
        
        @functools.wraps(func)
        async def wrapper(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, *args, **kwargs):
            await ctx.defer()
            return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def add_reaction(func):
        """
            Adds a reaction to the message at the end
        """
        @functools.wraps(func)
        async def wrapper(self, ctx: BridgeExtContext | BridgeApplicationContext, *args, **kwargs):
            if isinstance(ctx, BridgeExtContext):
                await ctx.message.add_reaction('👌')
            else:
                await command.respond(ctx, '👌')
            return await func(self, ctx, *args, **kwargs)
        return wrapper

    @staticmethod
    def delete_after(func):
        """
            Deletes the message five seconds after responding
        """
        @functools.wraps(func)
        async def wrapper(self, ctx: BridgeExtContext | BridgeApplicationContext, *args, **kwargs):
            value = await func(self, ctx, *args, **kwargs)
            try:
                if isinstance(ctx, BridgeExtContext):
                    await ctx.message.delete(delay=5)
                else:
                    await ctx.delete(delay=5)
            finally:
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
                caller = inspect.stack()[1].function
                func_name = func.__qualname__
                logger = logging.getLogger(f'self.{func_name}')
                logger.setLevel(level)
                logger.addHandler(handler)
                logger.info(f'Starting. Called by {caller}')
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
        async def wrapper(self, ctx: BridgeExtContext | BridgeApplicationContext, *args, **kwargs):
            server = ctx.guild.id
            if not server in self.tools.playlist:
                self.tools.playlist[server] = [[], []]
            if server not in self.tools.looping:
                self.tools.looping[server] = False
            return await func(self, ctx, *args, **kwargs)
        return wrapper


class Sync: # synchronous versions for synchronous functions

    @staticmethod
    def update_playlist(func):
        """
            Updates the playlist in the music bot commands
        """
        @functools.wraps(func)
        def wrapper(self, ctx: BridgeExtContext | BridgeApplicationContext, *args, **kwargs):
            server = ctx.guild.id
            if not server in self.tools.playlist:
                self.tools.playlist[server] = [[], []]
            if server not in self.tools.looping:
                self.tools.looping[server] = False
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
                caller = inspect.stack()[1].function
                func_name = func.__qualname__
                logger = logging.getLogger(f'self.{func_name}')
                logger.setLevel(level)
                logger.addHandler(handler)
                logger.info('starting')
                logger.info(f'Starting. Called by {caller}')
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