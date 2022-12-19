import bs4
from discord.ext import commands, bridge, pages
from requests_toolbelt import MultipartEncoder
from utility.common import config
from utility.cog.command import command_cog
from utility.common import decorators
from utility.common.errors import SauceNotFound
from utility.discord import target as discordutil
from utility.tools import sauce_tools

class sauce(commands.Cog, command_cog):
    """
        Finds the sauce (origin) from an image
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Finds the sauce from an image'
        self.fields = [
            ['url', '']
        ]
        rejected_dbs = [
            1, 4, 6, 7, 13, 14,
            17, 29, 34, 40, 42
        ]  # everything furry
        accepted_dbs = [str(db) for db in range(0, 44 + 1) if db not in rejected_dbs]
        self.fields += [['dbs[]', db] for db in accepted_dbs]

    @decorators.Async.logging.log
    async def get_sauce(self, url):
        try:
            fields = self.fields
            fields[0][1] = url
            data = MultipartEncoder(fields=fields)
            resp = await self.client.post(url='https://saucenao.com/search.php', data=data.to_string(), headers={'Content-Type': data.content_type})
            resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)
            hidden = soup.select('div #result-hidden-notification') != []
            results = soup.select('div.result') + soup.select('div.result.hidden')
            results = [result for result in results if 'onclick' not in result.attrs]
            if len(results) > 1:
                return results, hidden
            raise SauceNotFound()
        except:
            raise SauceNotFound()

    @bridge.bridge_command(help='url: optionally specify the url to the image')
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def sauce(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, url=None):
        if url == None:
            url = await discordutil.get_target(ctx, no_aud=True, no_vid=True)
            url = url.proxy_url
        results, hidden = await self.get_sauce(url)
        embeds = [sauce_tools.create_embed(res, url, hidden) for res in results]
        paginator = pages.Paginator(
            pages=embeds,
            loop_pages=True,
            disable_on_timeout=True
        )
        return await paginator.respond(ctx, paginator)
