from discord.ext import commands, bridge, pages
import discord
import urllib.request
import urllib.parse
import validators

from utility.tools.gogo_tools import create_search_result_embed, create_episode_results_embed
from utility.scraping import GogoAnime
from utility.common.errors import UrlInvalid
from utility.common import decorators, command
from itertools import zip_longest


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
            await command.respond(ctx, 'Number invalid. Try again.', ephemeral=True, delete_after=5)
            return await self._get_selected_index(ctx, length)
        return selected_index
    
    async def get_anime(self, ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext, message: discord.Message) -> str | None:
        search_query = await self._get_response_content(ctx)
        
        animes = await GogoAnime.search(search_query)
        if not animes:
            await command.respond(ctx, 'No animes found with the query %s' % search_query, mention_author=False)
            return None
        embeds = [create_search_result_embed(anime) for anime in animes]
        paginator = pages.Paginator(
            pages=embeds,
            timeout=None,
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
            timeout=None,
            author_check=False
        )
        await paginator.edit(message)
        await message.edit('Enter the number of the episode')
        
        episode_index = await self._get_selected_index(ctx, len(episodes))
        selected_episode = episodes[episode_index]

        return selected_episode.url
        
        
    @bridge.bridge_command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def gogo(
        self,
        ctx: bridge.BridgeApplicationContext | bridge.BridgeExtContext,
        url: bridge.core.BridgeOption(
            str,
            'The direct url to the anime episode ex. https://gogoanime.bid/steinsgate-episode-1'
        ) = None
    ) -> None:
        """
            Get a link to watch an episode of an anime without ads
        """
        if not url:
            message = await ctx.send('Enter the search query')
            try:
                url = await self.get_anime(ctx, message)
            except:
                url = None
            finally:
                await message.delete()
        if not url:
            return
        if not validators.url(url):
            raise UrlInvalid()
        
        try:
            m3u8_url = await GogoAnime.video_from_url(url)
        except:
            raise UrlInvalid()
        
        content = 'https://www.hlsplayer.org/play?url=' + urllib.parse.quote(m3u8_url)
        await command.respond(ctx, content)
