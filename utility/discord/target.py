from asyncio import AbstractEventLoop
import discord.embeds
from utility.common.errors import TargetNotFound
from discord.ext import commands
from discord import StickerItem, Embed, Attachment
from discord.embeds import EmbedProxy
from utility.ffprobe import FfprobeFormat, Ffprober
from utility.common import convert

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
    def __init__(self, loop : AbstractEventLoop, target : EmbedProxy | Attachment | StickerItem) -> None:
        self.loop = loop
        self.ffprober = Ffprober(loop)
        self.width = None
        self.height = None
        self.proxy_url = None
        self.type = None
        self.has_audio = None
        self.duration_s = None

        if isinstance(target, EmbedProxy):
            self.type = 'image'
        if isinstance(target, Attachment):
            self.type = target.content_type[:5]
        if isinstance(target, StickerItem):
            self.type = 'image'
            self.width = 320
            self.height = 320
            self.proxy_url = target.url
        elif target != None:
            self.proxy_url = target.proxy_url
            self.width = target.width
            self.height = target.height

    async def probe(self) -> None: # probes the target using ffprobe
        result = await self.ffprober.get_format(self.proxy_url)
        super().__init__(result)
        self.has_audio = self.nb_streams > 1
        self.duration_s = convert.timedelta.to_seconds(self.duration)

class target_fetcher:
    def __init__(self, no_aud=False, no_vid=False, no_img=False) -> None:
        self.aud = not no_aud
        self.vid = not no_vid
        self.img = not no_img

        self.allowed = lambda c: (
            c == 'audio' and self.aud) or (
            c == 'video' and self.vid) or (
            c == 'image' and self.img)

    def get_file(self, embeds : list[Embed], attachments : list[Attachment], stickers : list[StickerItem]) -> Embed | Attachment | StickerItem:
        for sticker in stickers:
            return sticker
        for attachment in attachments:
            if attachment.content_type != None:
                if self.allowed(attachment.content_type[:5]):
                    return attachment
        for embed in embeds:
            if isinstance(embed, discord.embeds.Embed):
                if isinstance(embed.video.proxy_url, str) and self.vid:
                    return embed.video
                if isinstance(embed.image.proxy_url, str) and self.img:
                    return embed.image
                if isinstance(embed.thumbnail.proxy_url, str) and self.img:
                    return embed.thumbnail
        return None

async def get_target(ctx : commands.Context, no_aud=False, no_vid=False, no_img=False) -> Target:
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
        return Target(ctx.bot.loop, file)
    raise TargetNotFound()