from discord.ext.bridge import BridgeExtContext, BridgeApplicationContext
from discord.ext.commands.context import Message
from discord.errors import HTTPException
from utility.common import decorators
import discord

@decorators.Async.logging.log
async def respond(
    ctx: BridgeExtContext| BridgeApplicationContext,
    /,
    content: str,
    *,
    file: discord.File = None,
    files: list[discord.File] = None,
    mention_author=False,
    **kwargs
) -> Message:
    """
        Safely respond to commands
    """
    kwargs['content'] = content
    if isinstance(ctx, BridgeExtContext):
        kwargs['mention_author'] = mention_author
        kwargs['file'] = file
        kwargs['files'] = files
    elif isinstance(ctx, BridgeApplicationContext):
        if files:
            kwargs['files'] = files
        elif file:
            kwargs['file'] = file 
    try:
        return await ctx.respond(**kwargs)
    except HTTPException as e:
        if isinstance(ctx, BridgeApplicationContext):
            return
    if file != None:
        file.fp.seek(0)
    if files != None:
        for i, _ in enumerate(files):
            files[i].fp.seek(0)
    return await ctx.channel.send(**kwargs)
    
    