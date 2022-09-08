import httpx

client = httpx.AsyncClient()

async def fetch_avatar(ctx):
    url = ctx.bot.user.avatar.url
    url = url.split('?')[0]
    resp = await client.get(url=url)
    resp.raise_for_status()
    return resp.content

async def fetch_webhook(ctx):
    webhooks = await ctx.message.channel.webhooks()
    for webhook in webhooks:
        if webhook.user.id == 955557550735106098:
            return webhook
    return await ctx.message.channel.create_webhook(name='サラボンボのすばらしいウエブフーック', avatar=await fetch_avatar(ctx))

async def send_message(ctx, embeds : list, files : list=None):
    webhook = await fetch_webhook(ctx)
    await webhook.send(embeds=embeds, files=files)