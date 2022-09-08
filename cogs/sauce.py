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
        proxies = await proxy.get_proxies()
        resp = await self.client(proxies=proxies, verify=False, timeout=None).post(url='https://saucenao.com/search.php', data=data.to_string(), headers={'Content-Type': data.content_type})
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.content, features='lxml')
        hidden = True if soup.select('div #result-hidden-notification') != [] else False
        if hidden:
            raise Exception('Sauce could not be found...')
        results = soup.select('div.result')
        return results

    @commands.command()
    async def sauce(self, ctx, url=None):
        if url == None:
            url = await discordutil.get_target(ctx, no_aud=True, no_vid=True)
            url = url.proxy_url
        results = await self.get_sauce(url)
        embed = sauce_tools.create_embed(results[0], url)
        message = await ctx.reply(embed=embed, mention_author=False)
        await message.edit(view=sauce_view(results=results, url=url))

def setup(client, tokens):
    client.add_cog(sauce(client))