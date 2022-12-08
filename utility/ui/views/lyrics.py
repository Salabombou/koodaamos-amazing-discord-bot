import discord
from utility.scraping.Genius import GeniusSearchResults
from utility.common.errors import LyricsTooLong
from utility.common import config
import asyncio

class lyrics_view(discord.ui.View):
    """
        View for lyrics search results
    """
    def __init__(self, message: discord.Message, results: GeniusSearchResults):
        super().__init__(timeout=30)
        self.message = message
        self.results = results
    
    def get_index(self):
        actionrow: discord.ActionRow = self.message.components[0]
        button: discord.Button = actionrow.children[2]
        return int(button.label.split('/')[0]) - 1
    
    @discord.ui.button(emoji='👆', style=discord.ButtonStyle.gray, row=0)
    async def select_lyrics_callback(self, button, interaction: discord.Interaction):
        """
            Responds with the lyrics and deletes the view from the message
        """
        lyrics = await self.results.song_results[self.get_index()].GetLyrics()
        if len(lyrics) + 6 > config.message.max_length:
            raise LyricsTooLong()
        await self.message.edit(view=None)
        await interaction.response.send_message(content=f'```{lyrics}```')