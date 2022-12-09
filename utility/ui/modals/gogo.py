import discord
from discord.ext import pages
from utility.common import config
from utility.scraping import GogoAnime
from itertools import zip_longest
import urllib.parse
import asyncio
from multiprocessing.pool import ThreadPool
from itertools import cycle

class search_modal(discord.ui.Modal):
    def __init__(self, client: discord.Client) -> None:
        self.client = client
        self.animes = None
        self.responses: list[discord.Message] = []
        super().__init__(timeout=None, title='GogoAnime Search')
        search_textbot = discord.ui.InputText(
            label='Search query here',
            style=discord.InputTextStyle.long,
            min_length=2,
            required=True
        )
        self.add_item(search_textbot)
    
    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
        return
    
    def _create_search_result_embed(self, anime: GogoAnime.AnimeItem) -> discord.Embed:
        embed = discord.Embed(
            title=anime.title,
            description=anime.url,
            color=config.embed.color
        )
        embed.set_image(url=anime.thumbnail)
        embed.set_footer(text=anime.release)
        
        return embed
    
    def _create_episode_results_embed(self, anime: GogoAnime.AnimeItem, episodes: list[GogoAnime.EpisodeItem]) -> discord.Embed:
        description = '\n'.join(
            [
                f'[Episode {str(episode.number).zfill(2)}]({episode.url})'
                    for episode in episodes
                        if episode != None
            ]
        )
        embed = discord.Embed(
            title=anime.title,
            description=description,
            color=config.embed.color
        )
        return embed
    
    async def _get_selected_index(self, interaction: discord.Interaction, length: int):
        result: discord.Message = await self.client.wait_for('message', check=lambda message: message.author ==  interaction.user)
        try:
            await result.delete()
        except: pass
        try:
            selected_index = abs(int(result.content)) - 1
            if not selected_index < length:
                raise ValueError()
        except ValueError:
            resp = await interaction.followup.send('Number invalid. Try again.', ephemeral=True)
            self.responses.append(resp.delete())
            return await self._get_selected_index(interaction, length)
        return selected_index
            
            
    async def callback(self, interaction: discord.Interaction):
        query = self.children[0].value
        self.animes = await GogoAnime.search(query)
        embeds = [self._create_search_result_embed(anime) for anime in self.animes]
        if embeds == []:
            return await interaction.response.send_message(f'No animes found with the query "{query}"', ephemeral=True)
        
        paginator = pages.Paginator(
            pages=embeds,
            disable_on_timeout=False,
            loop_pages=True
        )
        
        resp = await paginator.respond(interaction, ephemeral=True)
        self.responses.append(resp.delete())
        
        resp = await interaction.followup.send('Please enter the number of the anime', ephemeral=True)
        self.responses.append(resp.delete())
        
        anime_index = await self._get_selected_index(interaction, len(self.animes))

        selected_anime = self.animes[anime_index]
        
        episodes = await GogoAnime.get_episodes(selected_anime.url)
        episodes_chunks = list(zip_longest(*[iter(episodes)] * 25)) # splits the episodes list to 25 sized chunks. 3.12 is gonna make this simpler afaik
        
        embeds = [self._create_episode_results_embed(selected_anime, chunk[::-1]) for chunk in episodes_chunks]
        
        paginator = pages.Paginator(
            pages=embeds,
            disable_on_timeout=False,
            loop_pages=True,
        )
        resp = await paginator.respond(interaction, ephemeral=True)
        self.responses.append(resp.delete())
        
        resp = await interaction.followup.send('Please enter the number of the episode', ephemeral=True)
        self.responses.append(resp.delete())
        
        episode_index = await self._get_selected_index(interaction, len(episodes))
        
        selected_episode = episodes[episode_index]
        
        stream_url = await GogoAnime.video_from_url(selected_episode.url)
        
        link = 'https://www.hlsplayer.org/play?url=' + urllib.parse.quote(stream_url)
        
        with ThreadPool() as pool:
            args = zip(self.responses, cycle([self.client.loop]))
            pool.starmap(asyncio.run_coroutine_threadsafe, args)
        
        await interaction.followup.send(link)
