import discord
from discord.ext import commands
from utility import discordutil
import httpx
from requests_toolbelt import MultipartEncoder
import bs4
from utility.tools import sauce_tools
from utility.views.sauce import sauce_view
from utility.common.requests import proxy

class sauce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = httpx.AsyncClient

    async def get_sauce(self, url):
        fields = {
            'url': url
        }
        data = MultipartEncoder(fields=fields)
        selected_proxy = await proxy.get_proxy()
        resp = await self.client(proxies=selected_proxy, verify=False, timeout=10).post(url='https://saucenao.com/search.php', data=data.to_string(), headers={'Content-Type': data.content_type})
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.content, features='lxml')
        hidden = soup.select('div #result-hidden-notification') != []
        results = soup.select('div.result')
        if hidden:
            results = soup.select('div.result.hidden')
        if results != []:
            return results, hidden
        raise Exception('Could not find the sauce...')

    @commands.command()
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