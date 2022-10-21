from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Message


async def respond(ctx: commands.Context | ApplicationContext, *, mention_author=False, **kwargs) -> Message:
    if isinstance(ctx, ApplicationContext):
        return await ctx.respond(
            mention_author=mention_author,
            **kwargs
        )
    try:
        return await ctx.reply(
            mention_author=mention_author,
            **kwargs
        )
    except:
        return await ctx.send(
            mention_author=mention_author,
            **kwargs
        )
