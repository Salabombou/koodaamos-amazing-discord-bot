from discord.ext import commands
import discord
import asyncio
from discord import NotFound
from utility import VoiceChat, music_tools, common
import googleapiclient.discovery
import numpy as np
import math

class music(commands.Cog):
    def __init__(self, bot=None, tokens=None):
        self.bot = bot
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=tokens[3])
        self.playlist = {}
        self.looping = {}
        self.ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            }    

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def play(self, ctx, url='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau', *args):
        await VoiceChat.join(ctx)
        songs = await music_tools.fetch_songs(self, ctx, url, args)
        music_tools.play_song(self, ctx, songs)


    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    async def list(self, ctx):
        server = common.get_server(ctx)
        if not server in self.playlist:
            return
        embed = music_tools.create_embed(ctx, self.playlist, 0)
        message = await ctx.send(embed=embed)
        ctx = await self.bot.get_context(message)
        await message.edit(view=music_view(music_self=self, ctx=ctx))
        
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    async def disconnect(self, ctx):
        server = common.get_server(ctx)
        self.playlist[server] = [[],[]]
        await VoiceChat.leave(ctx)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    async def resume(self, ctx):
        if ctx.voice_client.is_paused():
            await VoiceChat.resume(ctx)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @common.decorators.add_reaction
    async def pause(self, ctx):
        if ctx.voice_client.is_playing():
            await VoiceChat.pause(ctx)
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def skip(self, ctx, amount='1'):
        server = common.get_server(ctx)
        temp = self.looping[server]
        self.looping[server] = False
        amount = abs(int(amount))
        del self.playlist[server][0][1:amount]
        music_tools.append_songs(ctx, self.playlist)
        await VoiceChat.stop(ctx) # skips one song
        await asyncio.sleep(0.5) #why? # just incase
        self.looping[server] = temp
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def shuffle(self, ctx):
        server = common.get_server(ctx)
        if self.playlist[server] == [[],[]]: return
        temp = self.playlist[server][0][0]
        self.playlist[server][0].pop(0)
        np.random.shuffle(self.playlist[server][0])
        np.random.shuffle(self.playlist[server][1])
        self.playlist[server][0].insert(0, temp)

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def loop(self, ctx):
        server = common.get_server(ctx)
        self.looping[server] = not self.looping[server]
    
    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    async def info(self, ctx, number='0'):
        await ctx.reply(embed=music_tools.create_info_embed(self, ctx))

    @commands.command()
    @commands.check(VoiceChat.command_check)
    @music_tools.decorators.update_playlist
    @common.decorators.add_reaction
    async def replay(self, ctx):
        server = common.get_server(ctx)
        self.playlist[server][0].insert(0, self.playlist[server][0][0])
        await VoiceChat.stop(ctx)

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
        self.server = common.get_server(ctx)
        self.children[0].options = music_tools.create_options(ctx, self.playlist)
        self.update_buttons()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.bot:
            return False # if the user is bot
        if interaction.user.voice == None:
            return False # if the user is not in the same voice chat
        if interaction.message.author.voice == None:
            return True # if the bot is not currently in a voice channel
        if interaction.user.voice.channel == interaction.message.author.voice.channel:
            return True # if the bot and the user are in the same voice channel

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
        await VoiceChat.stop(self.ctx)
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
            await VoiceChat.pause(self.ctx)
        else:
            await VoiceChat.resume(self.ctx)
        await interaction.response.edit_message(view=self)

def setup(client, tokens):
    client.add_cog(music(client, tokens))