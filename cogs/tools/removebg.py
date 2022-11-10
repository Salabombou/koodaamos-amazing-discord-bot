import base64
import json
import bs4
from discord.ext import commands
import httpx
from utility.common.command import respond
from utility.discord import target as discordutil
from utility.common import decorators
from utility.cog.command import command_cog
from requests_toolbelt import MultipartEncoder

class removebg(commands.Cog, command_cog):
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Removes the background from an image'

    async def get_csrf_token(self):
        resp = await self.client.get('https://www.remove.bg')
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.content, features='lxml')
        csrf_token = soup.select('meta[name="csrf-token"]')[0]['content']
        return csrf_token
        
    async def get_trust_token(self, csrf_token):
        headers = {
            'X-CSRF-Token': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
        }
        async with httpx.AsyncClient(cookies=None) as client:
            resp = await client.post(url='https://www.remove.bg/trust_tokens', headers=headers, data=None)
            resp.raise_for_status()
        resp_json = resp.json()
        trust_token: str = resp_json['request']
        trust_token = trust_token.split('(\'')[1][:-2]
        return trust_token
    
    async def get_result(self, csrf_token, trust_token, fileurl):
        fields = {
            'trust_token': trust_token,
            'image[original_source_url]': fileurl
        }
        data = MultipartEncoder(fields=fields)

        headers = {
            'Content-Type': data.content_type
        }
        url = 'https://www.remove.bg/images'
        resp = await self.client.post(url=url, data=data.to_string(), headers=headers)
        resp.raise_for_status()
        resp_json = resp.json()

        url = f"https://www.remove.bg{resp_json['url']}"
        headers = {
            'X-CSRF-Token': csrf_token,
            'X-Requested-With': 'XMLHttpRequest'
        }
        condition = True
        while condition:
            resp = await self.client.post(url=url, headers=headers)
            resp.raise_for_status()
            resp_json = resp.json()
            condition = 'fetch_in' in resp_json
        encoded_json = resp_json['pl']
        decoded_json = base64.decode(encoded_json)
        decoded_json = json.loads(decoded_json)
        result = decoded_json['result']['url']
        return result
        



    @commands.command(help='url: a link to the downloadable content (YouTube, Reddit, Tiktok, Spotify)')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.guild_only()
    @decorators.Async.typing
    async def removebg(self, ctx: commands.Context):
        target = await discordutil.get_target(ctx, no_aud=True, no_vid=True)
        csrf_token = await self.get_csrf_token()
        trust_token = await self.get_trust_token(csrf_token)
        result = await self.get_result(csrf_token, trust_token, target.proxy_url)
        await respond(ctx, content=result)

