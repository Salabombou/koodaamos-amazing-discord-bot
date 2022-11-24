from asyncio import AbstractEventLoop
from discord.ext import commands
import discord
import openai
import functools
from utility.common import decorators
from utility.common import config
import concurrent.futures
from utility.cog.command import command_cog


class gpt3(commands.Cog, command_cog):
    """
        An ai chatbot that can respond to different questions and tasks
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str]):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Outputs a response from a chat bot ai from the specified prompt'
        openai.api_key = self.tokens['openai']
        
    
    @decorators.Sync.logging.log
    def create_text(self, prompt):
        response = openai.Completion.create(
            engine='text-davinci-002',
            prompt=prompt + ':',
            temperature=0.5,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        text: str = response['choices'][0]['text']
        text = text.replace('\n\n', '\n')
        return text

    @commands.command(aliases=['text', 'ai'], help='prompt: the message to be sent to the ai')
    @commands.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.typing
    async def gpt3(self, ctx: commands.Context, *, prompt='make up a 4chan greentext post'):
        embed = discord.Embed(color=config.embed.color, fields=[], title=prompt)
        bot = ctx.bot
        loop: AbstractEventLoop = bot.loop
        with concurrent.futures.ThreadPoolExecutor() as pool:
            text = await loop.run_in_executor(pool, functools.partial(self.create_text, prompt=prompt))
        embed.description = f'```{text[:4090]}```'
        await ctx.reply(embed=embed)