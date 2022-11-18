import discord
from discord import Interaction
from utility.tools import sauce_tools


class sauce_view(discord.ui.View):
    def __init__(self, results, url, hidden):
        super().__init__(timeout=60)
        self.results = results
        self.url = url
        self.hidden = hidden
        self.index = 0
        self.update_index()
    
    async def on_timeout(self) -> None:
        await self.message.edit(view=None)
        
    def update_index(self):
        self.index = -1 if self.index + 1 > len(self.results) - 1 else self.index

    @discord.ui.button(label='◀', style=discord.ButtonStyle.gray)
    async def backward_callback(self, button, interaction: Interaction):
        self.index -= 1
        self.update_index()
        self.embed = sauce_tools.create_embed(
            self.results[self.index], self.url, self.hidden)
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.gray)
    async def forward_callback(self, button, interaction: Interaction):
        self.index += 1
        self.update_index()
        self.embed = sauce_tools.create_embed(self.results[self.index], self.url, self.hidden)
        return await interaction.response.edit_message(embed=self.embed, view=self)
