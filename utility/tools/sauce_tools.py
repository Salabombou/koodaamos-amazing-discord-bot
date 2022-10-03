import discord
import utility.common.string
from bs4 import BeautifulSoup
class parsed_result:
    def __init__(self, result : BeautifulSoup, hidden : bool):
        contents = result.select('div.resultcontent')[0]
        column = contents.select('div.resultcontentcolumn')[0]
        self.content = self.get_content(column)
        self.similarity = result.select('div.resultsimilarityinfo')[0].text

        title = '???'
        try: title = contents.select('div.resulttitle strong')[0].text
        except: pass
        self.title = title

        self.image = result.select('img')[0]

        if not 'data-src' in self.image.attrs:
            self.image = self.image['src']
        elif hidden:
            self.image = self.image['data-src']

    def get_content(self, column):
        def get_string(content):
            if content.name == 'strong':
                return content.text.strip() + ' '
            elif content.name == 'a':
                return f"[{content.text}]({content['href']})" + '\n'
            elif content.name == 'div':
                return content.text.strip() + '\n'
            elif isinstance(content, str):
                return content.strip() +'\n'
            return ''

        description = ''
        for content in column.contents:
            description += get_string(content)
        description = description[:-1]
        if description != '':
            return description
        return utility.common.string.zero_width_space()

def create_embed(result : BeautifulSoup, url : str, hidden : bool):
    result = parsed_result(result, hidden)
    embed = discord.Embed(title=result.title, fields=[], color=0xC9EDBE, description=result.content)
    embed.set_image(url=result.image)
    embed.set_footer(icon_url=url, text='Similarity: ' + result.similarity)
    return embed