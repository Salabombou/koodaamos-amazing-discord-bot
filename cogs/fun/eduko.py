import math
import threading
from discord.ext import commands
import discord
import httpx
import bs4
from utility.common.command import respond
import time
from utility.cog.command import command_cog

class eduko(commands.Cog, command_cog):
    def __init__(self, bot : commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.client = httpx.Client()
        self.description = 'Gets the Eduko diner menu for the week(s)'
        self.embeds = []
        self.updater = threading.Thread(target=self.update_food_embeds)
        self.updater.start()

    class Food:
        def __init__(self, p : bs4.BeautifulSoup):
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

        def get_food(self, p : bs4.BeautifulSoup):
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
        for week in weeks:
            embed = discord.Embed(color=0xC9EDBE, fields=[], title='VIIKKO ' + self.week_nums[0])
            week_spliced = self.splice_list(week, 2)
            for week in week_spliced:
                for food in week:
                    embed.add_field(name=food.header, value=food.the_actual_food, inline=False)
            embeds.append(embed)
            del self.week_nums[0]
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


    def update_food_embeds(self):
        while True:
            try:
                resp = self.client.get('https://www.eduko.fi/eduko/ruokalistat/')
            except: continue
            resp.raise_for_status()
            self.soup = bs4.BeautifulSoup(resp.content, features='lxml')
            self.week_nums = self.get_week_nums()
            self.sections = self.section_filter()
            self.foods = self.get_food()
            self.embeds = self.create_embeds()
            time.sleep(1000)

    @commands.command()
    async def food(self, ctx):
        await respond(ctx, embeds=self.embeds)