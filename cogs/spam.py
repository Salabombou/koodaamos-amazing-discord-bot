from discord.ext import commands
import asyncio

class spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spamming = {}
    
    async def spammy(self, ctx, server, content):
        if content != '':
            await asyncio.sleep(1)
            self.spamming[server] = True
        while self.spamming[server]:
            await ctx.send(content, delete_after=0.5)
            await asyncio.sleep(0.5)

    @commands.command()
    async def spam(self, ctx):
        if ctx.message.author.bot: return
        server = str(ctx.message.guild.id)
        if not server in self.spamming:
            self.spamming[server] = False
        content = ''
        for mention in ctx.message.mentions:
            content += f'<@{mention.id}> '
        self.spamming[server] = not self.spamming[server]
        asyncio.ensure_future(self.spammy(ctx, server, content))

def setup(client, tokens):
    client.add_cog(spam(client))