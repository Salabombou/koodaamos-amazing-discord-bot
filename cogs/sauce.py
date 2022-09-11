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
        rejected_dbs = [1,4,6,7.13,14,17,29,34,40,42]
        for i in range(0, 44 + 1):
            if not i in rejected_dbs:
                self.fields.append(['dbs[]', str(i)])
                
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
            results = soup.select('div.result') + soup.select('div.result.hidden')
            for result in results:
                if 'onclick' in result.attrs:
                    results.remove(result)
            if len(results) > 1:
                return results, hidden
            raise Exception()
        except:
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