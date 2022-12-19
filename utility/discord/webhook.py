import httpx
from discord.ext import commands
from discord import Embed, File, Webhook
from utility.common import decorators


client = httpx.AsyncClient()


async def __fetch_avatar(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> bytes:
    """
        Gets the bot's avatar from url
    """
    bot: commands.Bot = ctx.bot
    url = bot.user.avatar.url
    url = url.split('?')[0]
    resp = await client.get(url=url)
    resp.raise_for_status()
    return resp.content


async def _fetch_webhook(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> Webhook:
    """
        Gets the webhook from channel that is created by the bot. If it doesn't exists, creates one
    """
    webhooks = await ctx.message.channel.webhooks()
    for webhook in webhooks:
        if webhook.user.id != ctx.me.id:
            continue
        return webhook
    return await ctx.message.channel.create_webhook(name=f'{ctx.me.name}\'s Amazing Webhook', avatar=await __fetch_avatar(ctx))

@decorators.Async.logging.log
async def send_message(ctx, /, *, embeds: list[Embed], files: list[File] = None):
    """
        Sends a message using webhooks
    """
    webhook = await _fetch_webhook(ctx)
    await webhook.send(embeds=embeds, files=files)
