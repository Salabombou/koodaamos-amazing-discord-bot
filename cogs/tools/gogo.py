from discord.ext import commands, bridge, pages
import validators
import urllib.request
import urllib.parse
from utility.scraping import GogoAnime
from utility.common.errors import UrlInvalid
from utility.common import decorators
import discord
from utility.tools.gogo_tools import create_search_result_embed, create_episode_results_embed
from itertools import zip_longest
import asyncio


class gogo(commands.Cog):
    """
        Gets the anime's stream url from GogoAnime
    """
    def __init__(self, bot: bridge.Bot, tokens):
        self.bot = bot
    
    async def _get_response_content(self, ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext):
        response: discord.Message = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60.0)
        await response.delete()
        return response.content
    
    async def _get_selected_index(self, ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext, length: int) -> int:
        content = await self._get_response_content(ctx)
        try:
            selected_index = abs(int(content)) - 1
            if not selected_index < length:
                raise ValueError()
        except ValueError:
            await ctx.respond('Number invalid. Try again.', ephemeral=True, delete_after=5)
            return await self._get_selected_index(ctx, length)
        return selected_index
    
    async def get_anime(self, ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext) -> str:
        message = await ctx.send('Enter the search query')

        search_query = await self._get_response_content(ctx)
        
        animes = await GogoAnime.search(search_query)
        if not animes:
            return await ctx.respond('No animes found with the query %s' % search_query, mention_author=False)
        embeds = [create_search_result_embed(anime) for anime in animes]
        paginator = pages.Paginator(
            pages=embeds,
            timeout=60.0,
            disable_on_timeout=True,
            author_check=False # this is needed beucase its buggy atm pycord fix it
        )
        await paginator.edit(message)
        await message.edit('Enter the number of the anime')
        
        anime_index = await self._get_selected_index(ctx, len(animes))
        selected_anime = animes[anime_index]
        
        episodes = await GogoAnime.get_episodes(selected_anime.url)
        episodes_chunks = list(zip_longest(*[iter(episodes)] * 25)) # splits the episodes list to 25 sized chunks. 3.12 is gonna make this simpler afaik
        
        embeds = [create_episode_results_embed(selected_anime, chunk[::-1]) for chunk in episodes_chunks]
        paginator = pages.Paginator(
            pages=embeds,
            timeout=60.0,
            disable_on_timeout=True,
            author_check=False
        )
        await paginator.edit(message)
        await message.edit('Enter the number of the episode')
        
        episode_index = await self._get_selected_index(ctx, len(episodes))
        selected_episode = episodes[episode_index]
        
        asyncio.run_coroutine_threadsafe(
            message.delete(), self.bot.loop
        )
        
        return selected_episode.url
        
        
    @bridge.bridge_command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def gogo(self, ctx: bridge.BridgeContext, url: str = None):
        if not url:
            url = await self.get_anime(ctx)
        if not validators.url(url):
            raise UrlInvalid()
        
        try:
            m3u8_url = await GogoAnime.video_from_url(url)
        except:
            raise UrlInvalid()
        
        content = 'https://www.hlsplayer.org/play?url=' + urllib.parse.quote(m3u8_url)
        kwargs = {
            'content': content
        }
        if isinstance(ctx, bridge.BridgeExtContext):
            kwargs['mention_author'] = False
        await ctx.respond(**kwargs)
            
