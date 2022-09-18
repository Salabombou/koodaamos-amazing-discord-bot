async def respond(ctx, **kwargs):
    if not ctx.message:
        return await ctx.respond(**kwargs)
    try:
        return await ctx.reply(**kwargs)
    except:
        return await ctx.send(**kwargs)