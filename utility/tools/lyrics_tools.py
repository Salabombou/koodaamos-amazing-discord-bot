import discord
from utility.scraping import Genius
from utility.common import config

def create_embed(song_result: Genius.GeniusSearchResults.SongResult):
    embed = discord.Embed(color=config.embed.color, title=song_result.title)
    embed.set_image(url=song_result.thumbnail)
    embed.set_footer(icon_url=song_result.artist_icon, text=song_result.artist_names)
    embed.description = song_result.url
    return embed