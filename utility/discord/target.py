from asyncio import AbstractEventLoop
import asyncio
import functools
import discord.embeds
from utility.common.errors import TargetNotFound
from discord.ext import commands
from discord import StickerItem, Embed, Attachment
from utility.ffprobe import FfprobeFormat, Ffprober

"""
THE ORDER FOR THE FILES
    Sticker
    Attachment
    Embed
        Video
        Image
        Thumbnail

THE ORDER WHERE TO LOOK FOR FILES
    From the replied message
    From the command message itself
    From the channel history
"""

class Target(FfprobeFormat):
    def __init__(self, loop : AbstractEventLoop, target : Embed | Attachment | StickerItem) -> None:
        result = asyncio.run_coroutine_threadsafe(Ffprober.get_format(target.proxy_url), loop)
        result = result._result
        super().__init__(result)
        self.width = None
        self.height = None
        self.proxy_url = target.proxy_url
        self.type = None

        if isinstance(target, Embed):
            pass

class target_fetcher:
    def __init__(self, no_aud=False, no_vid=False, no_img=False) -> None:
        self.aud = not no_aud
        self.vid = not no_vid
        self.img = not no_img

        self.allowed = lambda c: (
            c == 'audio' and self.aud) or (
            c == 'video' and self.vid) or (
            c == 'image' and self.img)

    def get_file(self, embeds : list[Embed], attachments : list[Attachment], stickers : list[StickerItem]):
        for sticker in stickers:
            sticker.width = 320 # these attributes are missing from the StickerItem object
            sticker.height = 320
            sticker.proxy_url = sticker.url
            sticker.content_type = 'image'
            return sticker
        for attachment in attachments:
            if attachment.content_type != None:
                attachment.content_type = attachment.content_type[0:5]
                if self.allowed(attachment.content_type):
                    return attachment
        for embed in embeds:
            if isinstance(embed, discord.embeds.Embed):
                if isinstance(embed.video.proxy_url, str) and self.vid:
                    embed.video.content_type = 'video'
                    return embed.video
                if isinstance(embed.image.proxy_url, str) and self.img:
                    embed.image.content_type = 'image'
                    return embed.image
                if isinstance(embed.thumbnail.proxy_url, str) and self.img:
                    embed.image.content_type = 'image'
                    return embed.thumbnail
        return None

async def get_target(ctx : commands.Context, no_aud=False, no_vid=False, no_img=False):
    history = await ctx.channel.history(limit=100).flatten()
    fetcher = target_fetcher(no_aud, no_vid, no_img)
    stickers = ctx.message.stickers
    attachments = ctx.message.attachments
    file = fetcher.get_file([], attachments, stickers) # if there are embeds or attachments in the command itself
    
    for message in history[1:]: # first item in the list is likely the command
        if file != None: # if the target has been aquired
            break
        stickers = message.stickers
        attachments = message.attachments
        embeds = message.embeds
        file = fetcher.get_file(embeds, attachments, stickers)
    
    if ctx.message.reference != None:  # if its a reply
        reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        embeds = reply.embeds
        attachments = reply.attachments
        stickers = reply.stickers
        file = fetcher.get_file(embeds, attachments, stickers)

    if file != None:
        return file
    raise TargetNotFound()