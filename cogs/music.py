
from email.quoprimime import quote
from discord.ext import commands
import discord
import asyncio
from discord import NotFound
from utility import VoiceChat, YouTube
import urllib
from urllib.parse import parse_qs, urlparse
import googleapiclient.discovery
import numpy as np
import math
import isodate
import time
import validators

playlist = {}
looping = {}

def get_server(ctx):
    return str(ctx.message.guild.id)

class Video: # for the video info
    def __init__(self, data):
        self.title = data['title']
        self.description = data['description']
        self.channel = '???'
        self.thumbnail = None
        self.id = data['resourceId']['videoId']
        if data['title'] != 'Private video' and data['title'] != 'Deleted video': # if i can retrieve these stuff
            self.channel = data['channelTitle']
            self.thumbnail = data['thumbnails']['high']['url']
        #self.duration = '​'

async def serialize_songs(server):
    length = len(str(len(playlist[server]))) #cursed cast. todo fix whatever the fuck this is
    i = 0
    array = []
    for song in playlist[server]:
        dots = '...'
        digit = '0000000'[0:length - len(str(i))] + str(i) #dafuq .zfill()?
        if not len(song.title) > 34:
            dots = ''
        song = f"```{digit}: {song.title}"[0:44] + f'{dots}```'
        array.append(song)
        i += 1
    if len(array) <= 1:
        return ['']
    array.pop(0)
    return array

async def create_embed(ctx, page_num, youtube): # todo add timestamp
    server = get_server(ctx)
    embed = discord.Embed(title='PLAYLIST', description='', fields=[])
    index = page_num * 10
    songs = await serialize_songs(server)
    #currently_playing = Video() # zero width #BUT THERE IS NOT ?????
    if playlist[server] != []:
        currently_playing = playlist[server][0]
    for song in songs[index:10 + index][::-1]:
        embed.description += song# + '\n'
    embed.add_field(name='CURRENTLY PLAYING:', value=f'```{currently_playing.title}```')
    #embed.add_field(name='ENDS:', value=currently_playing.duration)
    return embed

class music(commands.Cog):
    def __init__(self, bot=None, tokens=None):
        self.bot = bot
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=tokens[3])
        self.ffmpeg_options = {
            'options': '-vn',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id: return
        if before.channel != None:
            if len(before.channel.members) == 1:
                playlist[str(before.channel.guild.id)] = []
                await before.channel.guild.voice_client.disconnect()

    def create_info_embed(self, ctx, number='0', song=None):
        server = get_server(ctx)
        if song == None:
            song = playlist[server][abs(int(number))]
        embed = discord.Embed(title=f'{song.title} - {song.channel}', description=song.description, fields=[])
        embed.set_image(url=song.thumbnail)
        return embed

    async def fetch_songs(self, ctx, url, args):        # todo get first song in list and play it, after that get rest
        if args != [] or not validators.url(url): # if there are more than 1 arguement or the url is invalid (implying for a search)
            search_query = f'{url} ' + ' '.join(args)
            song = YouTube.fetch_from_search(self.youtube, query=search_query)[0] # searches for the video and returns the url to it
            await ctx.reply(f"found a video with the query '{search_query}':", embed=self.create_info_embed(ctx, song=song))
            return [song]
        r = urllib.request.urlopen(url)
        url = r.url
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        if 'v' in query:
            return YouTube.fetch_from_video(self.youtube, videoId=query['v'][0])
        elif 'list' in query:
            return await YouTube.fetch_from_playlist(self.youtube, playlistId=query['list'][0])
        raise Exception('Invalid url')

    def play_song(self, ctx, songs=None):
        if ctx.voice_client == None:
            return
        server = get_server(ctx)
        if songs != None:
            playlist[server] += songs
        if not ctx.voice_client.is_playing() and playlist[server] != []:
            url = YouTube.get_raw_audio_url(f"https://www.youtube.com/watch?v={playlist[server][0].id}")
            source = discord.FFmpegPCMAudio(url, **self.ffmpeg_options)
            asyncio.run_coroutine_threadsafe(ctx.send('Currently playing:', embed=self.create_info_embed(ctx)), self.bot.loop)
            ctx.voice_client.play(discord.PCMVolumeTransformer(source, volume=0.1), after=lambda e: self.next_song(ctx))

    def next_song(self, ctx):
        server = get_server(ctx)
        if playlist[server] != []:
            if not looping[server]:
                playlist[server].pop(0)
            self.play_song(ctx)        

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play(self, ctx, url='https://youtube.com/playlist?list=PLxqk0Y1WNUGpZVR40HTLncFl22lJzNcau', *args):
        if ctx.message.author.bot:
            return
        server = get_server(ctx)
        await VoiceChat.join(ctx)
        songs = await self.fetch_songs(ctx, url, args)
        if not server in playlist:
                playlist[server] = []
                looping[server] = False
        await ctx.message.add_reaction('👌')
        self.play_song(ctx, songs)


    @commands.command()
    async def list(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        if not server in playlist:
            return
        embed = await create_embed(ctx, 0, self.youtube)
        message = await ctx.send(embed=embed)
        await message.edit(view=music_view(ctx=await self.bot.get_context(message), youtube=self.youtube))
        
    @commands.command()
    async def link(ctx):
        server = get_server(ctx)
        linked_message = await ctx.send("Currently playing " + str(playlist[server][0].title + "\n" + f"https://www.youtube.com/watch?v={playlist[server][0].id}"),delete_after=30)
    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        playlist[server] = []
        await VoiceChat.leave(ctx)
        await ctx.message.add_reaction('👌')

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client == None: return
        if ctx.voice_client.is_paused():
            await VoiceChat.resume(ctx)
            await ctx.message.add_reaction('👌')

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client == None: return
        if ctx.voice_client.is_playing():
            await VoiceChat.pause(ctx)
            await ctx.message.add_reaction('👌')
    
    @commands.command()
    async def skip(self, ctx, amount='1'):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        temp = looping[server]
        looping[server] = False
        for _ in range(1, abs(int(amount))): 
            try:
                playlist[server].pop(0)
            except:
                break
        await VoiceChat.stop(ctx) # skips one song
        await asyncio.sleep(0.5) #why? # just incase
        # also why do we not refresh the list after this. todo 
        looping[server] = temp
        await ctx.message.add_reaction('👌')
    
    @commands.command()
    async def shuffle(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        if playlist[server] == []: return
        temp = playlist[server][0]
        playlist[server].pop(0)
        np.random.shuffle(playlist[server])
        playlist[server].insert(0, temp)
        await ctx.message.add_reaction('👌')

    @commands.command()
    async def loop(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        looping[server] = not looping[server]
        await ctx.message.add_reaction('👌')
    
    @commands.command()
    async def info(self, ctx, number='0'):
        if ctx.voice_client == None: return
        await ctx.reply(embed=self.create_info_embed(ctx))

class music_view(discord.ui.View):
    def __init__(self, ctx, youtube):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.youtube = youtube
        self.embed = None
        self.index = 0
        self.server = get_server(ctx)
        self.update_buttons()
    
    async def on_error(self, error, item, interaction):
        if isinstance(error, NotFound):
            return
        embed = discord.Embed(color=0xFF0000, fields=[], title='Something went wrong!')
        embed.description = f'```{error}```'
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/992830317733871636.gif')
        await self.ctx.reply(embed=embed)
        await interaction.response.edit_message(view=self)

    def update_buttons(self): # holy fuck
        playlist_length = math.ceil(len(playlist[self.server]) / 10) - 1
        for i in range(0, len(self.children)):
            self.children[i].disabled = False

        if self.index == 0: # no more to go back
            self.children[0].disabled = True # super back
            self.children[1].disabled = True # back
        if self.index >= playlist_length: # no more to forward
            self.children[3].disabled = True # for
            self.children[4].disabled = True # super for
        if playlist[self.server] == []: # if the entire list is empty
            for i in range(0, len(self.children)):
                self.children[i].disabled = True
            self.children[3].disabled = False # refresh
            self.index = 0

    @discord.ui.button(label='FIRST PAGE' ,emoji='⏪', style=discord.ButtonStyle.red, row=0, disabled=True)
    async def super_backward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index = 0
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='PREVIOUS PAGE' ,emoji='◀️', style=discord.ButtonStyle.red, row=0, disabled=True)
    async def backward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index -= 1
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='REFRESH' ,emoji='🔄', style=discord.ButtonStyle.red, row=0)
    async def refresh_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='NEXT PAGE' ,emoji='▶️', style=discord.ButtonStyle.red, row=0)
    async def forward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index += 1
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LAST PAGE' ,emoji='⏩', style=discord.ButtonStyle.red, row=0)
    async def super_forward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index = math.ceil(len(playlist[self.server]) / 10) - 1
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SKIP' ,emoji='⏭️', style=discord.ButtonStyle.red, row=1)
    async def skip_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        temp = looping[self.server]
        looping[self.server] = False
        await VoiceChat.stop(self.ctx)
        await asyncio.sleep(0.5)
        looping[self.server] = temp
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SHUFFLE' ,emoji='🔀', style=discord.ButtonStyle.red, row=1)
    async def shuffle_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        if playlist[self.server] == []: return
        temp = playlist[self.server][0]
        playlist[self.server].pop(0)
        np.random.shuffle(playlist[self.server])
        playlist[self.server].insert(0, temp)
        self.embed = await create_embed(self.ctx, self.index, self.youtube)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LOOP' ,emoji='🔁', style=discord.ButtonStyle.red, row=1)
    async def loop_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        looping[self.server] = not looping[self.server]
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='PAUSE/RESUME' ,emoji='⏯️', style=discord.ButtonStyle.red, row=1)
    async def pauseresume_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        if not self.ctx.voice_client.is_paused():
            await VoiceChat.pause(self.ctx)
        else:
            await VoiceChat.resume(self.ctx)
        await interaction.response.edit_message(view=self)

def setup(client, tokens):
    client.add_cog(music(client, tokens))