import discord
from utility.scraping.Genius import GeniusSearchResults
from utility.common.errors import LyricsTooLong
from utility.common import embed_config
from utility.discord import message_config
import asyncio

class lyrics_view(discord.ui.View):
    """
        View for lyrics search results
    """
    def __init__(self, message: discord.Message, results: GeniusSearchResults):
        super().__init__(timeout=30)
        self.embeds = self.create_embeds(results.song_results)
        self.index = 0
        self.results = results
        self.loop = asyncio.get_running_loop()
        self.message = message
        asyncio.run_coroutine_threadsafe(
            message.edit(embed=self.embeds[0], content=''), self.loop
        )
    
    async def on_timeout(self) -> None:
        await self.message.edit(view=None)

    @staticmethod
    def create_embeds(song_results: list[GeniusSearchResults.SongResult]) -> list[discord.Embed]:
        """
            Creates the embeds from the lyrics
        """
        embeds = []
        for result in song_results:
            embed = discord.Embed(color=embed_config.color, title=result.title)
            embed.set_image(url=result.thumbnail)
            embed.set_footer(icon_url=result.artist_icon, text=result.artist_names)
            embed.description = f'URL: {result.url}'
            embeds.append(embed)
        return embeds
    
    def update_index(self):
        """
            Updates the index of the embeds
        """
        self.index = -1 if self.index + 1 > len(self.results.song_results) - 1 else self.index
    
    @discord.ui.button(label='◀', style=discord.ButtonStyle.gray)
    async def backward_callback(self, button, interaction: discord.Interaction):
        """
            Go backward
        """
        self.index -= 1
        self.update_index()
        await interaction.response.edit_message(embed=self.embeds[self.index])
    
    @discord.ui.button(label='▶', style=discord.ButtonStyle.gray)
    async def forward_callback(self, button, interaction: discord.Interaction):
        """
            Go forward
        """
        self.index += 1
        self.update_index()
        await interaction.response.edit_message(embed=self.embeds[self.index])
    
    @discord.ui.button(emoji='👆', style=discord.ButtonStyle.gray)
    async def select_lyrics_callback(self, button, interaction: discord.Interaction):
        """
            Responds with the lyrics and deletes the view from the message
        """
        lyrics = await self.results.song_results[self.index].GetLyrics()
        if len(lyrics) + 6 > message_config.max_length:
            raise LyricsTooLong()
        await self.message.edit(view=None)
        await interaction.response.send_message(content=f'```{lyrics}```')