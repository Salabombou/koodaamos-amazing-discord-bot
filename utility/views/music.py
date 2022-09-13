import discord
from discord import NotFound
from utility.discord import voice_chat
from utility.tools import music_tools
import math
import numpy as np
import asyncio


class music_view(discord.ui.View):
    def __init__(self, music_self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = music_self.bot
        self.playlist = music_self.playlist
        self.looping = music_self.looping
        self.youtube = music_self.youtube

        self.embed = None
        self.index = 0
        self.server = music_tools.get_server(ctx)
        self.children[0].options = music_tools.create_options(ctx, self.playlist)
        self.update_buttons()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.bot:
            return False # if the user is bot
        if interaction.user.voice == None:
            return False # if the user is not in the same voice chat
        if interaction.message.author.voice == None:
            return False # if the bot is not currently in a voice channel
        if interaction.user.voice.channel == interaction.message.author.voice.channel:
            return True # if the bot and the user are in the same voice channel
        return False

    async def on_error(self, error, item, interaction):
        if isinstance(error, NotFound):
            return
        embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
        embed.description = f'```{error}```'
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/992830317733871636.gif')
        await self.ctx.reply(embed=embed)
        await interaction.response.edit_message(view=self)

    def update_buttons(self): # holy fuck
        self.children[0].options = music_tools.create_options(self.ctx, self.playlist)
        playlist_length = math.ceil(len(self.playlist[self.server][0]) / 50)

        for child in self.children:
            child.disabled = False

        if self.index == 0: # no more to go back
            self.children[1].disabled = True # super back
            self.children[2].disabled = True # back
        if self.index >= playlist_length - 1: # no more to forward
            self.children[4].disabled = True # for
            self.children[5].disabled = True # super for
        if self.playlist[self.server][0] == []: # if the entire list is empty
            for child in self.children:
                child.disabled = True
            self.children[3].disabled = False # refresh
            self.index = 0

    def update_embed(self):
        for _ in range(0, self.index + 1):
            self.embed = music_tools.create_embed(self.ctx, self.playlist, self.index)
            if self.embed.description != '': break
            self.index -= 1
        
    @discord.ui.select(placeholder='Choose page...', min_values=0, row=0)
    async def select_callback(self, select, interaction):
        value = int(select.values[0])
        self.index = value
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='FIRST PAGE' ,emoji='⏪', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def super_backward_callback(self, button, interaction):
        self.index = 0
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='PREVIOUS PAGE' ,emoji='◀️', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def backward_callback(self, button, interaction):
        self.index -= 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='REFRESH' ,emoji='🔄', style=discord.ButtonStyle.red, row=1)
    async def refresh_callback(self, button, interaction):
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)
        
    @discord.ui.button(label='NEXT PAGE' ,emoji='▶️', style=discord.ButtonStyle.red, row=1)
    async def forward_callback(self, button, interaction):
        self.index += 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LAST PAGE' ,emoji='⏩', style=discord.ButtonStyle.red, row=1)
    async def super_forward_callback(self, button, interaction):
        self.index = math.ceil(len(self.playlist[self.server][0]) / 50) - 1
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SKIP' ,emoji='⏭️', style=discord.ButtonStyle.red, row=2)
    async def skip_callback(self, button, interaction):
        temp = self.looping[self.server]
        self.looping[self.server] = False
        await voice_chat.resume(self.ctx)
        await voice_chat.stop(self.ctx)
        await asyncio.sleep(0.5)
        self.looping[self.server] = temp
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SHUFFLE' ,emoji='🔀', style=discord.ButtonStyle.red, row=2)
    async def shuffle_callback(self, button, interaction):
        if self.playlist[self.server][0] == []: return
        temp = self.playlist[self.server][0][0]
        self.playlist[self.server][0].pop(0)
        np.random.shuffle(self.playlist[self.server][0])
        np.random.shuffle(self.playlist[self.server][1])
        self.playlist[self.server][0].insert(0, temp)
        self.update_embed()
        self.update_buttons()
        return await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LOOP' ,emoji='🔁', style=discord.ButtonStyle.red, row=2)
    async def loop_callback(self, button, interaction):
        self.looping[self.server] = not self.looping[self.server]
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='PAUSE/RESUME' ,emoji='⏯️', style=discord.ButtonStyle.red, row=2)
    async def pauseresume_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        if not self.ctx.voice_client.is_paused():
            await voice_chat.pause(self.ctx)
        else:
            await voice_chat.resume(self.ctx)
        await interaction.response.edit_message(view=self)
