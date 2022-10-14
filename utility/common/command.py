from discord.ext import commands
from discord.commands.context import ApplicationContext
from discord.ext.commands.context import Message


async def respond(ctx: commands.Context | ApplicationContext, mention_author=False, *args, **kwargs) -> Message:
    if isinstance(ctx, ApplicationContext):
        return await ctx.respond(
            *args,
            mention_author=mention_author,
            **kwargs
        )
    try:
        return await ctx.reply(
            *args,
            mention_author=mention_author,
            **kwargs
        )
    except:
        return await ctx.send(
            *args,
            mention_author=mention_author,
            **kwargs
        )
