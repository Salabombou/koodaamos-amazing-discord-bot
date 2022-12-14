from discord.ext import commands, bridge
import discord
import base64
import httpx
import json
import io

from utility.common import config, file_management, decorators, command
from utility.common.errors import AnimefierError
from utility.cog.command import command_cog
from utility.discord import target


class qq(commands.Cog, command_cog):
    """
        Uploads a facial image to the CCP and responds with it animefied with AI
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str, str]):
        super().__init__(bot=bot, tokens=tokens)
        self.url = 'https://ai.tu.qq.com/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process'
        self.image_to_base64 = lambda image: base64.b64encode(image).decode('utf-8')
    
    async def get_image_bytes(self, images: list[str]):
        if images == []:
            return
        try:
            image = await file_management.get_bytes(images[0])
        except:
            return await self.get_image_bytes(images[1:])
        return image
    
    async def get_animefied_images(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, /, *, image_url: str) -> list[str]:
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
    
    @bridge.bridge_command()
    @commands.cooldown(1, 60, commands.BucketType.default)
    @decorators.Async.typing
    @decorators.Async.defer
    async def animefy(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Use it at your own risk!
        """
        image = await target.get_target(ctx, no_aud=True, no_vid=True)
        
        animefied_images = await self.get_animefied_images(ctx, image_url=image.proxy_url)
        
        embed = discord.Embed(title='Animefied Image', fields=[], color=config.embed.color)
        embed.set_image(url='attachment://unknown.jpg')
        
        image = await self.get_image_bytes(images=animefied_images)
        file = discord.File(fp=io.BytesIO(image), filename='unknown.jpg')
        
        await command.respond(ctx, embed=embed, file=file)