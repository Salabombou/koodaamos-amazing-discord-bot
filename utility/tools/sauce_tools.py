import discord

class parsed_result:
    def __init__(self, result):
        contents = result.select('div.resultcontent')[0]
        column = contents.select('div.resultcontentcolumn')[0]
        self.image = result.select('img')[0]['src']
        self.similarity = result.select('div.resultsimilarityinfo')[0].text
        self.title = contents.select('div.resulttitle strong')[0].text
        self.content = self.get_content(column)

    def get_content(self, column):
        description = ''
        linebreak = False
        for content in column.contents:
            if content.name != 'br':
                end_of_line = '\n' if linebreak else ' '
                description += content.text + end_of_line
                linebreak = not linebreak
        return description[:-1]

def create_embed(result, url):
    result = parsed_result(result)
    embed = discord.Embed(title=result.title, fields=[], color=0xC9EDBE, description=f'```{result.content}```')
    embed.set_image(url=result.image)
    embed.set_footer(icon_url=url, text='Similarity: ' + result.similarity)
    return embed