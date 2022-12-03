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


class qq(commands.Cog, command_cog):
    """
        Morph images to look like anime
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str]):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Uploads an image to the CCP and responds with it animefied with AI'
        self.url = 'https://ai.tu.qq.com/trpc.shadow_cv.ai_processor_cgi.AIProcessorCgi/Process'
        self. image_to_base64 = lambda image: base64.b64encode(image).decode('utf-8')
    
    async def get_animefied_images(self, image_url: str) -> list[str]:
        resp = await self.client.get(image_url)
        resp.raise_for_status()
        image = self.image_to_base64(resp.content)
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
            raise AnimefierError(msg=resp_json['msg'])
        extra =  json.loads(resp_json['extra'])
        return extra['img_urls']
    
    @commands.command(help='Use it at your own risk!')
    @commands.cooldown(1, 180, commands.BucketType.default)
    @decorators.Async.typing
    async def animefy(self, ctx: commands.Context):
        image = await target.get_target(ctx, no_aud=True, no_vid=True)
        animefied_images = await self.get_animefied_images(image_url=image.proxy_url)
        embed = discord.Embed(title='Animefied Image', fields=[], color=config.embed.color)
        embed.set_image(url=animefied_images[0])
        await respond(ctx, embed=embed)