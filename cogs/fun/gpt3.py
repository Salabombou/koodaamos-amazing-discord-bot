from discord.ext import commands, bridge
from asyncio import AbstractEventLoop
import concurrent.futures
import functools
import discord
import openai

from utility.common import decorators, config, command

from utility.cog.command import command_cog


class gpt3(commands.Cog, command_cog):
    """
        An ai chatbot that can respond to different questions and tasks
    """
    def __init__(self, bot: commands.Bot, tokens: dict[str, str]):
        super().__init__(bot=bot, tokens=tokens)
        self.description = 'Outputs a response from a chat bot ai from the specified prompt'
        openai.api_key = self.tokens['openai']
        
    
    #@decorators.Sync.logging.log
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

    @bridge.bridge_command(aliases=['ai'])
    @bridge.is_nsfw()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def gpt3(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext,
        *,
        prompt: bridge.core.BridgeOption(
            str,
            'The message to be sent to the ai'
        ) = 'make up a 4chan greentext post'
    ) -> None:
        embed = discord.Embed(color=config.embed.color, fields=[], title=prompt)
        bot = ctx.bot
        loop: AbstractEventLoop = bot.loop
        with concurrent.futures.ThreadPoolExecutor() as pool:
            text = await loop.run_in_executor(pool, functools.partial(self.create_text, prompt=prompt))
        embed.description = f'```{text[:4090]}```'
        await command.respond(ctx, embed=embed)
