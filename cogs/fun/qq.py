from discord.ext import commands
from utility.common import decorators
from utility.cog.command import command_cog
import json
import base64
from utility.discord import target
import httpx
from utility.common.errors import AnimefierError
import discord
from utility.common import config
from utility.common.command import respond
from utility.common import file_management
import io



class qq(commands.Cog, command_cog):
    """
        Morph images to look like anime
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str]):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Uploads an image to the CCP and responds with it animefied with AI'
        self.url = 'https://ai.tu.qq.com/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process'
        self. image_to_base64 = lambda image: base64.b64encode(image).decode('utf-8')
    
    async def get_image_bytes(self, images: list[str]):
        if images == []:
            return
        try:
            image = await file_management.get_bytes(images[0])
        except:
            return await self.get_image_bytes(images[1:])
        return image
    
    async def get_animefied_images(self, ctx: commands.Context, /, *, image_url: str) -> list[str] | None:
        image = await file_management.get_bytes(file=image_url)
        image = self.image_to_base64(image)
        payload = {
            'busiId': 'ai_painting_anime_img_entry',
            'images': [
                image
            ]
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url=self.url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json['code'] != 0 and 'extra' not in resp_json:
            ctx.command.reset_cooldown(ctx)
            raise AnimefierError(msg=resp_json['msg'])
        elif 'extra' in resp_json:
            extra =  json.loads(resp_json['extra'])
            return extra['img_urls']
    
    @commands.command(help='Use it at your own risk!')
    @commands.cooldown(1, 60, commands.BucketType.default)
    @decorators.Async.typing
    async def animefy(self, ctx: commands.Context):
        image = await target.get_target(ctx, no_aud=True, no_vid=True)
        
        animefied_images = await self.get_animefied_images(ctx, image_url=image.proxy_url)
        
        embed = discord.Embed(title='Animefied Image', fields=[], color=config.embed.color)
        embed.set_image(url='attachment://unknown.jpg')
        
        image = await self.get_image_bytes(images=animefied_images)
        file = discord.File(fp=io.BytesIO(image), filename='unknown.jpg')
        
        await respond(ctx, embed=embed, file=file)