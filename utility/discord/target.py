from asyncio import AbstractEventLoop
from math import ceil
import discord.embeds
from utility.common.errors import TargetNotFound, TargetError
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
    def __init__(self, loop: AbstractEventLoop, target: Embed | Attachment | StickerItem) -> None:
        self.loop = loop
        self.ffprober = Ffprober(loop)
        self.width = None
        self.height = None
        self.width_safe = None
        self.height_safe = None
        self.proxy_url = None
        self.type = None
        self.has_audio = None
        self.is_audio = None
        self.duration_s = None
        self.size_bytes = None

        if isinstance(target, Embed):
            self.type = target.type
            target = self.get_embed_proxy(target)
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
        if self.width != None and self.height != None:
            self.width_safe = ceil(self.width / 2) * 2
            self.height_safe = ceil(self.height / 2) * 2
        else:
            self.width_safe = 1280
            self.height_safe = 720
        self.is_audio = self.type == 'audio'

    @staticmethod
    def get_embed_proxy(target: Embed):
        if isinstance(target.video.proxy_url, str):
            return target.video
        if isinstance(target.image.proxy_url, str):
            return target.image
        if isinstance(target.thumbnail.proxy_url, str):
            return target.thumbnail

    @staticmethod
    def get_factor(measurement) -> int:
        if measurement == 'byte':
            return 1
        if measurement == 'Kibyte':
            return 1000
        elif measurement == 'Mibyte':
            return 1000*1000
        else:
            raise TargetError('File size invalid')

    def get_bytes(self):
        digit, measurement = self.size.split()
        factor = self.get_factor(measurement)
        size_bytes = float(digit) * factor
        self.size_bytes = round(size_bytes)

    async def probe(self) -> None:  # probes the target using ffprobe
        result = await self.ffprober.get_format(self.proxy_url)
        super().__init__(**result)
        self.has_audio = self.nb_streams > 1 or self.type == 'audio'
        self.duration_s = convert.timedelta.to_seconds(
            self.duration
        ) if self.duration != None else 1
        self.get_bytes()


class target_fetcher:
    def __init__(self, no_aud=False, no_vid=False, no_img=False) -> None:
        self.aud = not no_aud
        self.vid = not no_vid
        self.img = not no_img

        self.allowed = lambda c: (
            c == 'audio' and self.aud) or (
            c == 'video' and self.vid) or (
            c == 'image' and self.img)

    def get_file(self, embeds: list[Embed], attachments: list[Attachment], stickers: list[StickerItem]) -> Embed | Attachment | StickerItem:
        for sticker in stickers:
            return sticker
        for attachment in attachments:
            if attachment.content_type != None:
                if self.allowed(attachment.content_type[:5]):
                    return attachment
        for embed in embeds:
            if isinstance(embed, Embed):
                if isinstance(embed.video.proxy_url, str) and self.vid:
                    return embed
                if isinstance(embed.image.proxy_url, str) and self.img:
                    return embed
                if isinstance(embed.thumbnail.proxy_url, str) and self.img:
                    return embed
        return None


async def get_target(ctx: commands.Context, no_aud=False, no_vid=False, no_img=False) -> Target:
    history = await ctx.channel.history(limit=100).flatten()
    fetcher = target_fetcher(no_aud, no_vid, no_img)
    stickers = ctx.message.stickers
    attachments = ctx.message.attachments
    # if there are embeds or attachments in the command itself
    file = fetcher.get_file([], attachments, stickers)

    for message in history[1:]:  # first item in the list is likely the command
        if file != None:  # if the target has been aquired
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
        target = Target(ctx.bot.loop, file)
        await target.probe()
        if target.size_bytes > 50 * 1000 * 1000:
            raise TargetError('File size too large')
        return target
    raise TargetNotFound()
