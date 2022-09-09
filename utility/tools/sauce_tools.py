import discord
import utility.common.string

class parsed_result:
    def __init__(self, result, hidden):
        contents = result.select('div.resultcontent')[0]
        column = contents.select('div.resultcontentcolumn')[0]
        self.similarity = result.select('div.resultsimilarityinfo')[0].text

        title = '???'
        try: title = contents.select('div.resulttitle strong')[0].text
        except: pass
        self.title = title

        self.image = result.select('img')[0]
        self.content = self.get_content(column)
        if not hidden:
            self.image = self.image['src']
        else:
            self.image = self.image['data-src']

    def get_content(self, column):
        def get_string(content):
            if content.name == 'strong':
                return content.text.rstrip() + ' '
            elif content.name in ['a', 'div']:
                return content.text.strip() + '\n'
            elif isinstance(content, str):
                return content.strip() + '\n'
            return ''

        description = ''
        for content in column.contents:
            if hasattr(content, 'contents'):
                for c in content.contents:
                    description += get_string(c)
            else:
                description += get_string(content)
        description = description[:-1]
        if description != '':
            return description
        return utility.common.string.zero_width_space()

def create_embed(result, url, hidden):
    result = parsed_result(result, hidden)
    embed = discord.Embed(title=result.title, fields=[], color=0xC9EDBE, description=f'```{result.content}```')
    embed.set_image(url=result.image)
    embed.set_footer(icon_url=url, text='Similarity: ' + result.similarity)
    return embed