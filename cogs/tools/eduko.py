from discord.ext import commands, bridge, pages
import discord
import math
import time
import bs4

from utility.common import decorators, config
from utility.cog.command import command_cog


class eduko(commands.Cog, command_cog):
    """
        Gets the Eduko's menu
    """
    def __init__(self, bot: commands.Bot, tokens):
        super().__init__(bot=bot, tokens=tokens)
        self.embeds = []
        self.paginator = None
        self.last_sync = 0
        self.foodlist_url = 'https://www.eduko.fi/eduko/ruokalistat/'

    class Food:
        def __init__(self, p: bs4.BeautifulSoup):
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

        def get_food(self, p: bs4.BeautifulSoup):
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
        foods = [food for food in foods if food.header != None]
        return foods

    def create_embeds(self):
        embeds = []
        weeks = self.splice_list(self.foods, 5)
        for week in weeks:
            embed = discord.Embed(
                color=config.embed.color,
                fields=[],
                title='VIIKKO ' + self.week_nums[0]
            )
            week_spliced = self.splice_list(week, 2)
            for week in week_spliced:
                for food in week:
                    embed.add_field(
                        name=config.string.zero_width_space + food.header,
                        value=config.string.zero_width_space + food.the_actual_food,
                        inline=False
                    )
            embeds.append(embed)
            del self.week_nums[0]
        return embeds

    def splice_list(self, arr, index) -> list[list[Food]]:
        spliced = []
        length = math.ceil(len(arr) / index)
        for _ in range(0, length):
            spliced.append(arr[:index])
            del arr[:index]
        return spliced

    def get_week_nums(self):
        week_nums = []
        h2_s = self.soup.select(
            'div .elementor-widget-container h2.elementor-heading-title.elementor-size-default'
        )
        for h2 in h2_s:
            text = str(h2.contents[0])
            if text.startswith('Viikko '):
                week_nums.append(text[7:])
        return week_nums
    
    #@decorators.Async.logging.log
    async def update_food_embeds(self):
        resp = await self.client.get(self.foodlist_url)
        resp.raise_for_status()

        self.soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)

        self.week_nums = self.get_week_nums()
        self.sections = self.section_filter()
        self.foods = self.get_food()

        self.embeds = self.create_embeds()
        self.paginator = pages.Paginator(
            pages=self.embeds,
            disable_on_timeout=True,
            loop_pages=True
        )
        self.last_sync = time.time()  # update the latest sync to current local time

    @bridge.bridge_command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @decorators.Async.typing
    @decorators.Async.defer
    async def food(
        self,
        ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext
    ) -> None:
        """
            Get the current menu(s) for the Eduko's lunch cafeteria
        """
        current_time = time.time()
        if current_time - self.last_sync > 1000:  # if it has been more than 1000 seconds since last sync
            await self.update_food_embeds()
        await self.paginator.respond(ctx)
