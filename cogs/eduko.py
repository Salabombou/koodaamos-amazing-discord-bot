from discord.ext import commands
from bs4 import BeautifulSoup
from utility import webhook
import httpx

class Food:
    def __init__(self, title, food):
        self.title = title
        self.food = food
        
async def GetStuff():
    async with httpx.AsyncClient() as requests:
        r = await requests.get('https://www.eduko.fi/eduko/ruokalistat/')
    soup = BeautifulSoup(r.content, features='lxml')
    sections = soup.find_all('section', {"class" : "elementor-section elementor-inner-section elementor-element elementor-element-70f81ef elementor-section-boxed elementor-section-height-default elementor-section-height-default"})
    foods = []
    for section in sections:
        dates = section.find_all('div', {'class': 'elementor-column elementor-col-50 elementor-inner-column elementor-element elementor-element-24a4cb1'})
        for date in dates:
            title = date.find('b').text
            date.find('b').decompose()
            food = date.text.replace('\n\n', '\n').split('\n')
            foods.append(Food(title=date.find, food='\n'.join(date[1:])))
    embeds = []
    for i in range(0, len(foods) / 5):
        embed = discord.Embed(color=0xC9EDBE, fields=[], title='RUOKALISTA')
        for food in foods[0:5]:
            embed.add_field(name=food.title, value=food.food, inline=True)
            food.pop(0)
        embed.add_field(name="​", value="​", inline=True)
        embeds.append(embed)
    return embeds

class eduko(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def food(self,ctx):
        async with ctx.channel.typing():
            embeds = await GetStuff()
            await webhook.send_message(ctx, embeds=embeds)
        return

def setup(client, tokens):
    client.add_cog(eduko(client))