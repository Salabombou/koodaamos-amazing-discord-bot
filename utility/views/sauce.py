import discord
from discord import Interaction
from utility.tools import sauce_tools
import asyncio

class sauce_view(discord.ui.View):
    def __init__(self, message: discord.Message, results, url, hidden):
        super().__init__(timeout=60)
        self.embeds = [sauce_tools.create_embed(result, url, hidden) for result in results]
        self.index = 0
        self.message = message
        self.loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(
            message.edit(embed=self.embeds[0], content=''),
            self.loop
        )
        self.update_index()
    
    async def on_timeout(self) -> None:
        await self.message.edit(view=None)
        
    def update_index(self):
        self.index = -1 if self.index + 1 > len(self.embeds) - 1 else self.index

    @discord.ui.button(label='◀', style=discord.ButtonStyle.gray)
    async def backward_callback(self, button, interaction: Interaction):
        self.index -= 1
        self.update_index()
        return await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label='▶', style=discord.ButtonStyle.gray)
    async def forward_callback(self, button, interaction: Interaction):
        self.index += 1
        self.update_index()
        return await interaction.response.edit_message(embed=self.embeds[self.index], view=self)
