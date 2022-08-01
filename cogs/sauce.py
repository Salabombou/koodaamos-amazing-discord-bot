import discord
from discord.ext import commands
from saucenao_api import SauceNao, VideoSauce, BookSauce, BasicSauce
from utility import discordutil
import aiohttp
import io
import os

#from discord import Button, ButtonStyle

async def GetImage(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return discord.File(os.getcwd() + "\\ERROR.gif", filename="ERROR.gif")
            return discord.File(io.BytesIO(await resp.read()), filename="thumbnail.jpg")

class sauce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def sauce(self, ctx):
        async with ctx.channel.typing():
            sauce = SauceNao(token) # sets the api_key for the sauce searcher
            isVideo = False
            result = None
            try:
                url = await discordutil.GetFileUrl(ctx, no_vid=True, no_aud=True)
                result = sauce.from_url(url)[0]
            except Exception as e:
                await ctx.reply("Something went wrong!\n```" + str(e) + "\n```")
                return
            embed = discord.Embed(color=0xC9EDBE, fields=[], title=result.title)
            embed.add_field(name="CONFIDENCE: ", value=str(result.similarity), inline=False)
            if isinstance(result, VideoSauce): # from a video ex. anime
                isVideo = True
                embed.add_field(name="EPISODE: ", value=str(result.part), inline=False)
                embed.add_field(name="YEAR: ", value=str(result.year), inline=False)
                embed.add_field(name="AT: ",  value=str(result.est_time), inline=False)
            elif isinstance(result, BookSauce): # from a book ex. manga
                embed.add_field(name="CHAPTER: ", value=str(result.part), inline=False)
            else:
                try:
                    embed.add_field(name="AUTHOR: ", value=str(result.author), inline=False)
                except:
                    embed.add_field(name="AUTHOR: ", value='​', inline=False)
            try:
                if "https://e621.net" in result.urls[0] or "https://www.furaffinity.net" in result.urls[0]:
                    await ctx.reply("EWW FURRY PORN GET O U T!!!!!!!!!!!!!!!!!!", mention_author=False)
                    return
                msg = result.urls[0]
            except:
                msg = ""
            embed.set_thumbnail(url=result.thumbnail)
            await ctx.reply(msg, embed=embed, mention_author=False)

def setup(client, tokens):
    global bot
    global token
    token = tokens[1]
    bot = client
    client.add_cog(sauce(client))