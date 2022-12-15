from discord.ext.bridge import BridgeExtContext, BridgeApplicationContext
from discord.ext.commands.context import Message
from discord.errors import HTTPException
from utility.common import decorators
import discord

@decorators.Async.logging.log
async def respond(
    ctx: BridgeExtContext| BridgeApplicationContext, /, *,
    file: discord.File = None,
    files: list[discord.File] = None,
    mention_author=False,
    **kwargs
) -> Message:
    """
        Safely respond to commands
    """
            
    try:
        return await ctx.respond(
            mention_author=mention_author,
            file=file,
            files=files,
            **kwargs
        )
    except HTTPException as e:
        status = e.status
        if not isinstance(ctx, BridgeExtContext):
            return
        if status != 400 and status != 404:
            return

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
    
    