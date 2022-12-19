from discord.ext import commands, bridge
from asyncio import AbstractEventLoop
import concurrent.futures
from PIL import Image
import discord
import base64
import httpx
import json
import io

from utility.cog.command import command_cog
from utility.common import decorators, config


class dalle(commands.Cog, command_cog):
    """
        Creates a 3x3 collage from ai generated images from a prompt
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)

    @decorators.Async.logging.log
    async def DallE_Collage(self, loop: AbstractEventLoop, arg):
        images = await self.CreateImages(prompt=arg)
        images = self.ConvertImages(images)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            collage = await loop.run_in_executor(pool, self.CreateCollage, images)
            collage = await loop.run_in_executor(pool, self.PillowImageToBytes, collage)
        return collage

    async def CreateImages(self, prompt):
        condition = True
        async with httpx.AsyncClient(timeout=90) as client:
            while condition:
                r = await client.post(headers={'Content-Type': 'application/json'}, data=json.dumps({'prompt': prompt}), url='https://backend.craiyon.com/generate')
                condition = r.status_code == 524
        r.raise_for_status()
        return r.json()['images']

    def ConvertImages(self, images) -> Image.Image:
        for image in images:
            image = str.encode(image)  # encodes string to bytes
            image = base64.decodebytes(image)  # decodes base64 to bytes image
            image = Image.open(io.BytesIO(image))  # opens the image in PIL
            yield image  # yields the finished image
    
    def CreateCollage(self, images: list):
        collage = Image.new("RGBA", (3072, 3072))
        for y in range(0, 3072, 1024):
            for x in range(0, 3072, 1024):
                collage.paste(next(images), (x, y))
        return collage

    @staticmethod
    def PillowImageToBytes(image: Image.Image):
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return buf

    @bridge.bridge_command()
    @bridge.is_nsfw()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def dalle(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        prompt: bridge.core.BridgeOption(
            str,
            'The message to be sent to the ai'
        ) = 'a cute kitten'
    ) -> None:
        """
            Create an image collage from images produced by an AI from a prompt
        """
        embed = discord.Embed(color=config.embed.color, fields=[], title=prompt)
        embed.set_image(url="attachment://unknown.png")
        image = await self.DallE_Collage(self.bot.loop, prompt)
        file = discord.File(fp=image, filename="unknown.png")
        await ctx.respond(embed=embed, file=file)
