from discord.ext import commands
import discord
import openai
import asyncio

def CreateText(arg):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=arg + ':',
        temperature=0.5,
        max_tokens=256,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
        )
    text = response["choices"][0]["text"]
    text = text.replace('\n\n', '\n')
    return text
    
class gpt3(commands.Cog):
    def __init__(self, bot, tokens):
        self.bot = bot
        self.tokens = tokens
        openai.api_key = self.tokens[1]

    @commands.command(aliases=["text", "ai"])
    @commands.is_nsfw()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gpt3(self, ctx, *, arg="make up a 4chan greentext post"):
        if ctx.message.author.bot:
            return
        embed = discord.Embed(color=0xC9EDBE, fields=[], title=arg)   
        async with ctx.typing():
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, CreateText, arg)
        embed.description = f'```{text}```'
        await ctx.reply(embed=embed, mention_author=False)

def setup(client, tokens):
    client.add_cog(gpt3(client, tokens))