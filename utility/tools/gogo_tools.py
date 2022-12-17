from utility.scraping import GogoAnime
import discord
from utility.common import config



def create_search_result_embed(anime: GogoAnime.AnimeItem) -> discord.Embed:
    embed = discord.Embed(
        title=anime.title,
        description=anime.url,
        color=config.embed.color
    )
    embed.set_image(url=anime.thumbnail)
    embed.set_footer(text=anime.release)
        
    return embed
    
def create_episode_results_embed(anime: GogoAnime.AnimeItem, episodes: list[GogoAnime.EpisodeItem]) -> discord.Embed:
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