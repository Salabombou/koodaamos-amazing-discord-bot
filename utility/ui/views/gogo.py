import discord
from utility.ui.modals.gogo import search_modal
from utility.common import config

class anime_search_view(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
    
    @discord.ui.button(emoji=config.emoji.index_pointing_up, style=discord.ButtonStyle.gray, row=0)
    async def select_button_callback(self, button, interaction: discord.Interaction):
        await interaction.response.send_modal(search_modal())
        pass
    