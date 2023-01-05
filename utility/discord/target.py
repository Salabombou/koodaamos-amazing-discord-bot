from asyncio import AbstractEventLoop
from math import ceil
from utility.common.errors import TargetNotFound, TargetError
from discord.ext import bridge
from discord import StickerItem, Embed, Attachment
from utility.ffprobe import FfprobeFormat, Ffprober
from utility.common import convert, decorators

import httpx


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
    """
        The class object for targeted files in discord
    """
    def __init__(self, loop: AbstractEventLoop, target: Embed | Attachment | StickerItem) -> None: 
        self.loop = loop
        self.ffprober = Ffprober(loop)
        self.width = None
        self.height = None
        self.width_safe = None
        self.height_safe = None
        self.url = target.url
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
            if target.content_type:
                self.type = target.content_type.split('/')[0]
            else:
                self.type = target.filename.split('.')[-1]
            
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
        """
            Gets the proxy url from the embed
        """
        if isinstance(target.video.proxy_url, str):
            return target.video
        if isinstance(target.image.proxy_url, str):
            return target.image
        if isinstance(target.thumbnail.proxy_url, str):
            return target.thumbnail

    @staticmethod
    def get_factor(measurement: str) -> int:
        """
            Gets the right factor from str
        """
        if measurement == 'byte':
            return 1
        if measurement == 'Kibyte':
            return 1000
        if measurement == 'Mibyte':
            return 1000_000
        raise TargetError('File size invalid')

    def get_bytes(self) -> None:
        """
            Gets the size of the file in bytes
        """
        digit, measurement = self.size.split()
        factor = self.get_factor(measurement)
        size_bytes = float(digit) * factor
        self.size_bytes = round(size_bytes)

    async def probe(self) -> None:
        """
            Probes the target using ffprobes
        """
        if self.type not in ['image', 'video', 'audio']:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.url)
            resp.raise_for_status()
            self.size_bytes = len(resp.content)
            return
        result = await self.ffprober.Probe(self.proxy_url)
        super().__init__(**result.__dict__)
        self.has_audio = self.nb_streams > 1 or self.type == 'audio'
        self.duration_s = convert.timedelta.to_seconds(
            self.duration
        ) if self.duration != None else 1
        self.get_bytes()


class target_fetcher:
    """
        Fetcher used to fetch target from discord
    """
    def __init__(self, ext: str, no_aud=False, no_vid=False, no_img=False) -> None:
        self.aud = not no_aud
        self.vid = not no_vid
        self.img = not no_img
        self.ext = ext

        self.allowed = lambda c: (
            c == 'audio' and self.aud) or (
            c == 'video' and self.vid) or (
            c == 'image' and self.img)

    def get_file(self, embeds: list[Embed], attachments: list[Attachment], stickers: list[StickerItem]) -> Embed | Attachment | StickerItem:
        """
            Gets the targeted file
        """
        for sticker in stickers:
            return sticker if not self.ext else None
        for attachment in [a for a in attachments if a.content_type != None or self.ext]:
            file_ext = attachment.filename.split('.')[-1]
            if file_ext[-len(self.ext):] == self.ext:
                return attachment
            if self.ext:
                continue
            if self.allowed(attachment.content_type.split('/')[0]):
                return attachment
        if self.ext:
            return
        for embed in [e for e in embeds if isinstance(e, Embed)]:
            if isinstance(embed.video.proxy_url, str) and self.vid:
                return embed
            if isinstance(embed.image.proxy_url, str) and self.img:
                return embed
            if isinstance(embed.thumbnail.proxy_url, str) and self.img:
                return embed

#@decorators.Async.logging.log
async def get_target(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, ext: str = None, no_aud=False, no_vid=False, no_img=False) -> Target:
    """
        Gets the target from the discord chat
    """
    history = await ctx.channel.history(limit=100).flatten()
    fetcher = target_fetcher(ext, no_aud, no_vid, no_img)
    reference = None
    file = None

    if ctx.message:
        stickers = ctx.message.stickers
        attachments = ctx.message.attachments
        # if there are embeds or attachments in the command itself
        file = fetcher.get_file([], attachments, stickers)
        
    for message in history[1:]:  # first item in the list is likely the command
        if file:  # if the target has been aquired
            break
        stickers = message.stickers
        attachments = message.attachments
        embeds = message.embeds
        file = fetcher.get_file(embeds, attachments, stickers)

    if ctx.message.reference:  # if its a reply
        reply = ctx.message.reference.resolved
        embeds = reply.embeds
        attachments = reply.attachments
        stickers = reply.stickers
        file = fetcher.get_file(embeds, attachments, stickers)
    if file:
        target = Target(ctx.bot.loop, file)
        await target.probe()
        if target.size_bytes > 8_000_000: # change to whatever you are comfortable with or what your pc would be win
            raise TargetError('File size too large')
        return target
    raise TargetNotFound()
