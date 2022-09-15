import asyncio
import math
from discord.ext import commands
import discord
import httpx
import bs4

class eduko(commands.Cog):
    def __init__(self, bot):
        self.description = 'Gets the Eduko diner menu for the week(s)'
        self.client = httpx.AsyncClient()
        self.embeds = []
        self.bot = bot
        asyncio.ensure_future(self.update_embeds())

    class Food:
        def __init__(self, p):
            self.header = None
            self.the_actual_food = None
            spans = p.select('span')
            bs = p.select('b')
            for spam in spans:
                self.header = spam.text
                self.the_actual_food = self.get_food(p)
            for b in bs:
                self.header = b.text
                self.the_actual_food = self.get_food(p)

        def get_food(self, p):
            food = ''
            for content in p.contents:
                if isinstance(content, str):
                    food += content + '\n'
            return food
    
    def section_filter(self):
        sections = self.soup.select('section')
        for section in sections:
            divs = section.select('div .elementor-container.elementor-column-gap-narrow')
            if 'data-settings' in section or divs == []:
                sections.remove(section)
        sections = sections[6:-2]
        return sections

    def get_food(self):
        foods = []
        for section in self.sections:
            for p in section.select('p'):
                foods.append(self.Food(p))
        for food in foods:
            if food.header == None:
                foods.remove(food)
        return foods

    def create_embeds(self):
        embeds = []
        weeks = self.splice_list(self.foods, 5)
        for week in weeks[::-1]:
            embed = discord.Embed(color=0xC9EDBE, fields=[], title='VIIKKO ' + self.week_nums[-1])
            week_spliced = self.splice_list(week, 2)
            for week in week_spliced:
                for food in week:
                    embed.add_field(name=food.header, value=food.the_actual_food, inline=False)
            embeds.append(embed)
            del self.week_nums[-1]
        return embeds

    def splice_list(self, arr, index):
        spliced = []
        length = math.ceil(len(arr) / index)
        for _ in range(0, length):
            spliced.append(arr[:index])
            del arr[:index]
        return spliced
    
    def get_week_nums(self):
        week_nums = []
        h2s= self.soup.select('div .elementor-widget-container h2.elementor-heading-title.elementor-size-default')
        for h2 in h2s:
            text = str(h2.contents[0])
            if text.startswith('Viikko '):
                week_nums.append(text[7:])
        return week_nums


    async def update_embeds(self):
        while True:
            resp = await self.client.get('https://www.eduko.fi/eduko/ruokalistat/')
            resp.raise_for_status()
            self.soup = bs4.BeautifulSoup(resp.content, features='lxml')
            self.week_nums = self.get_week_nums()
            self.sections = self.section_filter()
            self.foods = self.get_food()
            self.embeds = self.create_embeds()
            await asyncio.sleep(1000)

    @commands.slash_command()
    async def food(self, ctx):
        await ctx.respond(embeds=self.embeds)

def setup(client, tokens):
    client.add_cog(eduko(client))