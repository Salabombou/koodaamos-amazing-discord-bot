from discord.ext import commands
import discord
import openai

from utility.common import decorators

def CreateText(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt + ':',
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
        self.description = 'Outputs a response from a chat bot ai from the specified prompt'
        self.bot = bot
        self.tokens = tokens
        openai.api_key = self.tokens[1]

    @commands.command(aliases=["text", "ai"], help='prompt: the message to be sent to the ai')
    @commands.is_nsfw()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @decorators.typing
    async def gpt3(self, ctx, *, prompt="make up a 4chan greentext post"):
        embed = discord.Embed(color=0xC9EDBE, fields=[], title=prompt)   
        loop = ctx.bot.loop
        text = await loop.run_in_executor(None, CreateText, prompt)
        embed.description = f'```{text}```'
        await ctx.reply(embed=embed, mention_author=False)

def setup(client, tokens):
    client.add_cog(gpt3(client, tokens))