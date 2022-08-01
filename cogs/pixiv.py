from discord.ext import commands
import discord
from pixivpy3 import *
import os
import subprocess
import asyncio

async def GetTags(tags):
    string = ''
    for tag in tags:
        string += tag.name + ', '
    return string[:len(string) - 2]  

async def GetImage(self):
    imgurl = self.results[self.index].image_urls.large
    server = str(self.ctx.message.guild.id)
    user = str(self.ctx.message.author.id)
    user_path = '{}\\{}\\'.format(server, user)
    path = os.getcwd() + '\\files\\pixiv\\' + user_path
    img = self.api.requests_call("GET", imgurl, headers={"Referer": "https://app-api.pixiv.net/"}, stream=True)
    if not os.path.exists(path):
        os.makedirs(path)
    file_path = path + str(self.results[self.index].id) + '.jpg'
    f = open(file_path, 'wb')
    for chunk in img:
        f.write(chunk)
    f.close()
    return file_path

async def CreateEmbed(self):
    result = self.results[self.index]
    embed = discord.Embed(color=0xC9EDBE, fields=[], title=result.title)
    embed.add_field(name='USER: ', value=result.user.name)
    embed.add_field(name='DATE CREATED: ', value=result.create_date)
    tags = await GetTags(result.tags)
    embed.add_field(name='TAGS: ', value=tags)
    image = 'https://embed.pixiv.net/artwork.php?illust_id={}'.format(str(result.id))
    embed.set_image(url=image)
    return embed

async def UpdateButtons(self):
    index = self.index
    length = len(self.results)
    if not index < length - 1: # no more to forward
        self.children[0].disabled = False
        self.children[1].disabled = False
        self.children[2].disabled = True
        self.children[3].disabled = True
    elif index == 0: # no more to go back
        self.children[0].disabled = True
        self.children[1].disabled = True
        self.children[2].disabled = False
        self.children[3].disabled = False
    else:
        self.children[0].disabled = False
        self.children[1].disabled = False
        self.children[2].disabled = False
        self.children[3].disabled = False
    self.children[4].disabled = True
    if self.downloaded[self.index] == False:
        self.children[4].disabled = False
    return self
class View(discord.ui.View): # Create a class called View that subclasses discord.ui.View
    def __init__(self, msg, results, ctx, api):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.user_path = '{}\\{}\\'.format(str(ctx.message.guild.id), str(ctx.message.author.id))
        self.message = msg
        self.results = results
        self.index = 0
        self.api = api
        self.downloaded = [False] * len(results)
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        directory = os.getcwd() + '\\files\\pixiv\\' + self.user_path
        for f in os.listdir(directory):
            os.remove(os.path.join(directory, f))
        await self.message.edit(view=self)
       
    @discord.ui.button(emoji='⏮️', style=discord.ButtonStyle.green, disabled=True)
    async def rewind_button_callback(self, button, interaction):
        self.index = 0
        embed = await CreateEmbed(self)
        self = await UpdateButtons(self)
        await interaction.response.edit_message(embed=embed, view=self)
        pass
    @discord.ui.button(emoji='◀️', style=discord.ButtonStyle.green, disabled=True)
    async def backward_button_callback(self, button, interaction):
        self.index -= 1
        embed = await CreateEmbed(self)
        self = await UpdateButtons(self)
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(emoji='▶️', style=discord.ButtonStyle.green)
    async def forward_button_callback(self, button, interaction):
        self.index += 1
        embed = await CreateEmbed(self)
        self = await UpdateButtons(self)
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(emoji='⏭️', style=discord.ButtonStyle.green)
    async def fast_forward_button_callback(self, button, interaction):
        self.index = len(self.results) - 1
        embed = await CreateEmbed(self)
        self = await UpdateButtons(self)
        await interaction.response.edit_message(embed=embed, view=self)
    @discord.ui.button(label="Download full picture", style=discord.ButtonStyle.green)
    async def download_button_callback(self, button, interaction):
        image = await GetImage(self)
        self.children[4].disabled = True
        self.downloaded[self.index] = True
        await self.message.edit(view=self)
        await interaction.response.send_message(file=discord.File(image))    
        
class pixiv(commands.Cog):
    def __init__(self, bot, token):
        self.bot = bot
        self.api = AppPixivAPI()
        self.api.auth(refresh_token=token)
    

    @commands.command()
    async def pixiv(self, ctx, *, arg="おかゆ"):
        results = self.api.search_illust(arg).illusts
        if results == None: return
        result = results[0]
        embed = discord.Embed(color=0xC9EDBE, fields=[], title=result.title)
        embed.add_field(name='USER: ', value=result.user.name)
        embed.add_field(name='DATE CREATED: ', value=result.create_date)
        tags = await GetTags(result.tags)
        embed.add_field(name='TAGS: ', value=tags)
        image = 'https://embed.pixiv.net/artwork.php?illust_id={}'.format(str(results[0].id))
        embed.set_image(url=image)
        message = await ctx.reply(embed=embed)
        await message.edit(view=View(msg=message, results=results, ctx=ctx, api=self.api))

def setup(client, tokens):
    file = os.getcwd() + '/files/pixiv_token'
    TOKEN = open(file, 'r').read()
    cmd = 'python {}\\files\\pixiv_auth.py refresh {}'.format(os.getcwd(), TOKEN)
    subprocess.Popen(cmd, shell=True).wait()
    TOKEN = open(file, 'r').read()
    client.add_cog(pixiv(client, TOKEN))