from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Message
from utility.common import decorators
import discord

@decorators.Async.logging.log
async def respond(
    ctx: commands.Context | ApplicationContext, /, *,
    file: discord.File = None,
    files: list[discord.File] = None,
    mention_author=False,
    **kwargs
) -> Message | None:
    """
        Safely respond to commands
    """
    if isinstance(ctx, ApplicationContext):
        return await ctx.respond(
            mention_author=mention_author,
            file=file,
            files=files,
            **kwargs
        )
        
    try: 
        return await ctx.message.reply(
            mention_author=mention_author,
            file=file,
            files=files,
            **kwargs
        )
    except: # message to reply was most likely deleted
        pass
     
    if file != None:
        file.fp.seek(0)
    if files != None:
        for i, _ in enumerate(files):
            files[i].fp.seek(0)
             
    return await ctx.channel.send(
        mention_author=mention_author,
        file=file,
        files=files,
        **kwargs
    )