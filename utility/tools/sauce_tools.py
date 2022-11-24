import bs4
import discord
from utility.common import config
from bs4 import BeautifulSoup
from utility.common import config

class parsed_result:
    """
        Gets the parsed results 
    """
    def __init__(self, result: BeautifulSoup, hidden: bool):
        contents = result.select_one('div.resultcontent')
        column = contents.select_one('div.resultcontentcolumn')
        self.content = self.get_content(column)
        self.similarity = result.select_one('div.resultsimilarityinfo').text

        title = '???'
        try:
            title = contents.select_one('div.resulttitle strong').text
        except:
            pass
        self.title = title

        self.image = result.select_one('img')

        if not 'data-src' in self.image.attrs:
            self.image = self.image['src']
        elif hidden:
            self.image = self.image['data-src']

    def get_content(self, column: bs4.BeautifulSoup):
        """
            Gets the content from the SauceNao document
        """
        def get_string(content: bs4.BeautifulSoup):
            if content.name == 'strong':
                return content.text.strip() + ' '
            elif content.name == 'a':
                return f"[{content.text}]({content['href']})" + '\n'
            elif content.name == 'div':
                return content.text.strip() + '\n'
            elif isinstance(content, str):
                return content.strip() + '\n'
            return ''

        description = ''
        for content in column.contents:
            description += get_string(content)
        description = description[:-1]
        if description != '':
            return description
        return config.string.zero_width_space


def create_embed(res: bs4.BeautifulSoup, url: str, hidden: bool):
    """
        Creates the embed for the sauce
    """
    result = parsed_result(res, hidden)
    embed = discord.Embed(
        title=result.title,
        fields=[],
        color=config.embed.color,
        description=result.content
    )
    embed.set_image(url=result.image)
    embed.set_footer(icon_url=url, text='Similarity: ' + result.similarity)
    return embed
