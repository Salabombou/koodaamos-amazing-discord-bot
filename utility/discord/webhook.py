import httpx
from discord.ext.commands.context import Context
from discord import Embed, File
client = httpx.AsyncClient()

async def fetch_avatar(ctx : Context):
    url = ctx.bot.user.avatar.url
    url = url.split('?')[0]
    resp = await client.get(url=url)
    resp.raise_for_status()
    return resp.content

async def fetch_webhook(ctx : Context):
    webhooks = await ctx.message.channel.webhooks()
    for webhook in webhooks:
        if webhook.user.id == 955557550735106098:
            return webhook
    return await ctx.message.channel.create_webhook(name='サラボンボのすばらしいウエブフーック', avatar=await fetch_avatar(ctx))

async def send_message(ctx, embeds : list[Embed], files : list[File] = None):
    webhook = await fetch_webhook(ctx)
    await webhook.send(embeds=embeds, files=files)