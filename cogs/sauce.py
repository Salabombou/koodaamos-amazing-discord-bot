import discord
from discord.ext import commands
from utility import discordutil
import httpx
from requests_toolbelt import MultipartEncoder
import bs4
from utility.tools import sauce_tools
from utility.views.sauce import sauce_view
from utility.common.requests import proxy
from utility.common import decorators
import json

class sauce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = httpx.AsyncClient
        self.fields = [
            ['url', '']
        ]
        for i in ['0','2','3','5','8','9','10','11','12','15','16','18','19','20','21','22','23','24','25','26','27','28','30','31','32','33','35','36','37','38','39','41','43','44']:
            self.fields.append(['dbs[]', i])
            
    async def get_sauce(self, url):
        try:
            fields = self.fields
            fields[0][1] = url
            data = MultipartEncoder(fields=fields)
            selected_proxy = proxy.get_proxy()
            resp = await self.client(proxies=selected_proxy).post(url='https://saucenao.com/search.php', data=data.to_string(), headers={'Content-Type': data.content_type})
            resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features='lxml')
            hidden = soup.select('div #result-hidden-notification') != []
            results = soup.select('div.result')
            if hidden:
                results = soup.select('div.result.hidden')
            if  len(results) > 1:
                return results, hidden
            raise Exception()
        except Exception as e:
            print(str(e))
            raise Exception('Could not find the sauce...')

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.typing
    async def sauce(self, ctx, url=None):
        if url == None:
            url = await discordutil.get_target(ctx, no_aud=True, no_vid=True)
            url = url.proxy_url
        results, hidden = await self.get_sauce(url)
        embed = sauce_tools.create_embed(results[0], url, hidden=hidden)
        message = await ctx.reply(embed=embed, mention_author=False)
        await message.edit(view=sauce_view(results=results, url=url, hidden=hidden))

def setup(client, tokens):
    client.add_cog(sauce(client))