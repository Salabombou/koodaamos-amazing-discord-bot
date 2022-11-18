from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Message
from discord import NotFound

async def respond(ctx: commands.Context | ApplicationContext, /, *, mention_author=False, **kwargs) -> Message | None:
    if isinstance(ctx, ApplicationContext):
        return await ctx.respond(
            mention_author=mention_author,
            **kwargs
        )
    message = None
    try:
        message = await ctx.reply(
            mention_author=mention_author,
            **kwargs
        )
    except NotFound:
        message = await ctx.send(
            mention_author=mention_author,
            **kwargs
        )
    finally:
        return message
