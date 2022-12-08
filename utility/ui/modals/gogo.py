import discord
from discord.ext import pages
from utility.common import config
from utility.scraping import GogoAnime

class search_modal(discord.ui.Modal):
    def __init__(self) -> None:
        self.animes = None
        super().__init__(timeout=None, title='GogoAnime Search')
        search_textbot = discord.ui.InputText(
            label='Search query here',
            style=discord.InputTextStyle.long,
            min_length=2,
            required=True
        )
        self.add_item(search_textbot)
    
    
    def _create_embed(self, anime: GogoAnime.SearchItem) -> discord.Embed:
        embed = discord.Embed(
            title=anime.title,
            color=config.embed.color
        )
        embed.set_image(url=anime.thumbnail)
        embed.set_footer(text=anime.release)
        
        return embed
    
    async def callback(self, interaction: discord.Interaction):
        query = self.children[0].value
        self.animes = await GogoAnime.search(query)
        embeds = [self._create_embed(anime) for anime in self.animes]
        if embeds == []:
            return await interaction.response.send_message(f'No animes found with the query "{query}"')
        paginator = pages.Paginator(
            pages=embeds,
            disable_on_timeout=True,
            loop_pages=True
        )
        await paginator.respond(interaction)
    