from discord.ext import commands
import urllib
import validators

class download(commands.Cog):
    def __init__(self, bot, tokens):
        self.bot = bot
        self.acceptable_hosts = [
            'youtube.com'
        ]
        #self.token = tokens[0]

    @commands.command()
    async def dl(self, ctx, url=None):
        if url != None and validators.url(url):
            resp = urllib.request.urlopen(url)
            parsed = urllib.parse.urlparse(resp.url)
            host = parsed.hostname
            pass


def setup(client, tokens):
    client.add_cog(download(client, tokens))