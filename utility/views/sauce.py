import discord
from utility.tools import sauce_tools

class sauce_view(discord.ui.View):
    def __init__(self, results, url, hidden):
        super().__init__(timeout=60)
        self.results = results
        self.url = url
        self.hidden = hidden
        self.index = 0

    def update_buttons(self):
        self.children[0].disabled = self.index - 1 <= 0
        self.children[1].disabled = self.index + 1 >= len(self.results)

    @discord.ui.button(label='LAST RESULT ◀', style=discord.ButtonStyle.gray, disabled=True)
    async def backward_callback(self, button, interaction):
        self.index -= 1
        self.embed = sauce_tools.create_embed(self.results[self.index], self.url, self.hidden)
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='NEXT RESULT ▶', style=discord.ButtonStyle.gray)
    async def forward_callback(self, button, interaction):
        self.index += 1
        self.embed = sauce_tools.create_embed(self.results[self.index], self.url, self.hidden)
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)
