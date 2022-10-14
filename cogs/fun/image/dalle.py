from asyncio import AbstractEventLoop
from discord.ext import commands
import httpx
from utility.common import decorators
from PIL import Image
import discord
import base64
import json
import io
from utility.cog.command import command_cog
import concurrent.futures

class dalle(commands.Cog, command_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Creates an image collage from images produced by an AI with a prompt'

    async def DallE_Collage(self, loop: AbstractEventLoop, arg):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            images = await self.CreateImages(prompt=arg)
            images = await loop.run_in_executor(pool, self.ConvertImages, images)
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

    def ConvertImages(self, images):
        imgs = []
        for image in images:
            image = str.encode(image)  # encodes string to bytes
            # decodes the base64 data to bytes image
            image = base64.decodebytes(image)
            image = Image.open(io.BytesIO(image))  # opens the image in PIL
            # appends the finished image to the imgs array
            imgs.append(image)
        return imgs

    def CreateCollage(self, images: list):
        collage = Image.new("RGBA", (768, 768))
        for y in range(0, 768, 256):
            for x in range(0, 768, 256):
                # pastes the images to a white canvas in 9x9 alignment
                collage.paste(images[0], (x, y))
                images.pop(0)
        return collage

    def PillowImageToBytes(self, image: Image):
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return buf

    @commands.command(help='prompt: the message to be sent to the ai')
    @commands.is_nsfw()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def dalle(self, ctx: commands.Context, *, prompt="a cute kitten"):
        embed = discord.Embed(color=0xC9EDBE, fields=[], title=prompt)
        embed.set_image(url="attachment://unknown.png")
        image = await self.DallE_Collage(ctx.bot.loop, prompt)
        file = discord.File(fp=image, filename="unknown.png")
        await ctx.reply(embed=embed, file=file)
