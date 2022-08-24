from discord.ext import commands
from PIL import Image
import asyncio
import zipfile
import discord
import base64
import httpx
import json
import io

class View(discord.ui.View):
    def __init__(self, message, zippy):
        super().__init__(timeout=180)
        self.message = message
        self.zippy = zippy

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
        
    @discord.ui.button(label="Get invidual images", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        for child in self.children:
            child.disabled = True
        file = discord.File(fp=self.zippy, filename='images.zip')
        await interaction.response.send_message("Here are all the images invidually!", file=file)
        await self.message.edit(view=self)

class dalle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = httpx.AsyncClient(timeout=180)

    async def DallE_Collage(self, loop, arg):
        images = await self.CreateImages(prompt=arg)
        images = await loop.run_in_executor(None, self.ConvertImages, images, )
        zippy = await loop.run_in_executor(None, self.CreateZip, images)
        collage = await loop.run_in_executor(None, self.CreateCollage, images)
        collage = await loop.run_in_executor(None, self.PillowImageToBytes, collage)
        return collage, zippy

    async def CreateImages(self, prompt):
        condition = True
        while condition:
            r = await self.client.post(headers={'Content-Type': 'application/json'}, data=json.dumps({'prompt': prompt}), url='https://backend.craiyon.com/generate')
            condition = r.status_code == 524
        r.raise_for_status()
        return r.json()['images']
    
    def ConvertImages(self, images):
        imgs = []
        for image in images:
            image = str.encode(image)             # encodes string to bytes
            image = base64.decodebytes(image)     # decodes the base64 data to bytes image
            image = Image.open(io.BytesIO(image)) # opens the image in PIL
            imgs.append(image)                    # appends the finished image to the imgs array
        return imgs

    def CreateCollage(self, images):
        collage = Image.new("RGBA", (768, 768))
        for y in range(0, 768, 256):
            for x in range(0, 768, 256):
                collage.paste(images[0], (x, y)) # pastes the images to a white canvas in 9x9 alignment
                images.pop(0)
        return collage

    def PillowImageToBytes(self, image):
        buf = io.BytesIO()
        image.save(buf, format='PNG')
        buf.seek(0)
        return buf

    def CreateZip(self, images):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'a') as zippy:
            i = 1
            for image in images:
                image = self.PillowImageToBytes(image)
                zippy.writestr(f'image{i}.png', image.getvalue())
                i += 1
        buf.seek(0)
        return buf

    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def dalle(self, ctx, *, arg="a cute kitten"):
        if ctx.message.author.bot:
            return
        async with ctx.typing():
            embed = discord.Embed(color=0xC9EDBE, fields=[], title=arg)
            embed.set_image(url="attachment://unknown.png")
            image, zip = await self.DallE_Collage(ctx.bot.loop, arg)
            file = discord.File(fp=image, filename="unknown.png")
            message = await ctx.reply(embed=embed, file=file)
            await message.edit(view=View(message=message, zippy=zip))
        
def setup(client, tokens):
    client.add_cog(dalle(client))