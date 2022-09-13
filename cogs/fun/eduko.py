import asyncio
import math
from discord.ext import commands
import discord
import httpx
import bs4
import datetime
import time

from utility.discord import webhook

#from utility import webhook

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
class eduko(commands.Cog):
    def __init__(self, bot):
        self.description = 'Gets the Eduko diner menu for the week(s)'
        self.client = httpx.AsyncClient()
        self.embeds = []
        self.bot = bot
        asyncio.ensure_future(self.update_embeds())

    def section_filter(self, soup):
        sections = soup.select('section')
        for section in sections:
            divs = section.select('div .elementor-container.elementor-column-gap-narrow')
            if 'data-settings' in section or divs == []:
                sections.remove(section)
        sections = sections[6:-2]
        return sections

    def get_food(self, sections):
        foods = []
        for section in sections:
            for p in section.select('p'):
                foods.append(Food(p))
        for food in foods:
            if food.header == None:
                foods.remove(food)
        return foods

    def create_embeds(self, foods):
        embeds = []
        weeks = self.splice_list(foods, 5)
        seconds = 0
        for week in weeks:
            embed = discord.Embed(color=0xC9EDBE, fields=[], title='VIIKKO ' + self.get_week_num(seconds))
            week_spliced = self.splice_list(week, 2)
            for week in week_spliced:
                for food in week:
                    embed.add_field(name=food.header, value=food.the_actual_food, inline=False)
            embed.add_field(name='​', value='​', inline=True)
            embeds.append(embed)
            seconds += 604800
        return embeds
    
    def splice_list(self, arr, index):
        spliced = []
        length = math.ceil(len(arr) / index)
        for _ in range(0, length):
            spliced.append(arr[:index])
            del arr[:index]
        return spliced

    def get_week_num(self, seconds):
        timestamp = math.ceil(time.time()) + seconds
        week_num = str(datetime.date.fromtimestamp(timestamp).isocalendar().week)
        return week_num

    async def update_embeds(self):
        while True:
            resp = await self.client.get('https://www.eduko.fi/eduko/ruokalistat/')
            resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features='lxml')
            sections = self.section_filter(soup)
            foods = self.get_food(sections)
            self.embeds = self.create_embeds(foods)
            await asyncio.sleep(100)

    @commands.command()
    async def food(self,ctx):
        await webhook.send_message(embeds=self.embeds, ctx=ctx)

def setup(client, tokens):
    client.add_cog(eduko(client))