
from turtle import dot
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
import validators

playlist = {}
looping = {}

def get_server(ctx):
    return str(ctx.message.guild.id)

def append_songs(ctx, songs=[]): # appends songs to the playlist
    server = get_server(ctx)
    length = len(playlist[server][0])
    playlist[server][1] += songs
    playlist[server][0] += playlist[server][1][0:1000 - length] # limits the visible playlist to go to upto 1000 song at once
    del playlist[server][1][0:1000 - length]

def get_duration(youtube, videoId): # youtube api v3 needs a v4
    request = youtube.videos().list(
        part='contentDetails',
        id=videoId
    )
    r = request.execute()
    duration = 'PT2S'
    try:
        duration = r['items'][0]['contentDetails']['duration']
    except: pass
    duration = isodate.parse_duration(duration)
    return duration.seconds # returns the duration of the song that was not included in the snippet for some reason

def serialize_songs(server):
    length = len(str(len(playlist[server][0][0:101]))) #cursed cast. todo fix whatever the fuck this is # it just works trust me bro
    i = 0
    songs = []
    for song in playlist[server][0]:
        digit = f'{i}'.zfill(length)
        title = song.title[0:30]
        title_length = len(title)
        if title_length == 30 :
            title += ' ...'
        song = f'**{digit}**: {title}'
        songs.append(song)
        i += 1
    if len(songs) <= 1:
        return ['']
    songs.pop(0)
    return songs

def create_embed(ctx, page_num): # todo add timestamp
    server = get_server(ctx)
    embed = discord.Embed(title='PLAYLIST', description='', fields=[], color=0xC4FFBD)
    index = page_num * 50
    playlist_length = math.ceil(len(playlist[server][0]) / 50)
    songs = serialize_songs(server)
    if playlist[server][0] != []:
        currently_playing = playlist[server][0][0]
    for song in songs[index:50 + index][::-1]:
        embed.description += song + '\n'
    embed.add_field(name='CURRENTLY PLAYING:', value=f'```{currently_playing.title}```')
    embed.set_footer(text=f'Showing song(s) in the playlist queue from page {page_num+1}/{playlist_length} out of {len(playlist[server][0])} song(s) in the queue') # bigggggg
    return embed

def create_options(ctx):
    server = get_server(ctx)
    page_amount = math.ceil(len(playlist[server][0]) / 50)
    options = []
    for i in range(0, page_amount):
        options.append(
            discord.SelectOption(
                label=f'Page {i+1}',
                description='',
                value=str(i)
                )
            )
    return options

class music(commands.Cog):
    def __init__(self, bot=None, tokens=None):
        self.bot = bot
        self.youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=tokens[3])
        self.ffmpeg_options = {
            'options': '-vn -af "asplit[a],aphasemeter=video=0,ametadata=select:key=lavfi.aphasemeter.phase:value=-0.005:function=less,pan=1c|c0=c0,aresample=async=1:first_pts=0,[a]amix"',
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            }

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id: return
        if before.channel != None:
            if len(before.channel.members) == 1:
                server = str(before.channel.guild.id)
                playlist[server] = [[],[]]
                await before.channel.guild.voice_client.disconnect()

    def create_info_embed(self, ctx, number='0', song=None):
        server = get_server(ctx)
        if song == None:
            song = playlist[server][0][abs(int(number))]
        embed = discord.Embed(title=song.title, description=song.description, fields=[], color=0xC4FFBD)
        embed.set_image(url=song.thumbnail)
        embed.add_field(name='LINKS:', value=f'\n\n[Video](https://www.youtube.com/watch?v={song.id})\n[Channel](https://www.youtube.com/channel/{song.channelId})')
        icon = YouTube.fetch_channel_icon(youtube=self.youtube, channelId=song.channelId)
        embed.set_footer(text=song.channel, icon_url=icon)
        return embed

    async def fetch_songs(self, ctx, url, args):        # todo get first song in list and play it, after that get rest
        if args != () or not validators.url(url): # if there are more than 1 arguement or the url is invalid (implying for a search)
            search_query = f'{url} ' + ' '.join(args)
            song = YouTube.fetch_from_search(self.youtube, query=search_query)[0] # searches for the video and returns the url to it
            embed = self.create_info_embed(ctx, song=song)
            await ctx.reply(f"found a video with the query '{search_query}':", embed=embed, delete_after=10)
            return [song]
        r = urllib.request.urlopen(url)
        url = r.url
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        if 'v' in query:
            return YouTube.fetch_from_video(self.youtube, videoId=query['v'][0])
        elif 'list' in query:
            song = await YouTube.fetch_from_playlist(self.youtube, playlistId=query['list'][0])
            async def fetch_the_rest():
                await asyncio.sleep(0.5) # just incase
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=query['list'][0],
                    maxResults=1000
                )
                items = []
                while request != None:
                    r = await ctx.bot.loop.run_in_executor(None, request.execute)
                    items += r['items']
                    request = self.youtube.playlistItems().list_next(request, r)
                songs = []
                for song in items[1:]:
                    song = song['snippet']
                    songs.append(YouTube.Video(data=song))
                append_songs(ctx, songs)
            asyncio.ensure_future(fetch_the_rest()) # fire and forget
            return [song]
        raise Exception('Invalid url')

    def play_song(self, ctx, songs=[]):
        if ctx.voice_client == None:
            return
        server = get_server(ctx)
        append_songs(ctx, songs)
        if not ctx.voice_client.is_playing() and playlist[server][0] != []:
            song = playlist[server][0][0]
            url = YouTube.get_raw_audio_url(f'https://www.youtube.com/watch?v={song.id}')
            source = discord.FFmpegPCMAudio(url, **self.ffmpeg_options)
            embed = self.create_info_embed(ctx)
            message = asyncio.run_coroutine_threadsafe(ctx.send('Now playing:', embed=embed), self.bot.loop)
            ctx.voice_client.play(discord.PCMVolumeTransformer(source, volume=0.75), after=lambda e: self.next_song(ctx, message._result))

    def next_song(self, ctx, message):
        server = get_server(ctx)
        try:
            asyncio.run_coroutine_threadsafe(message.delete(), self.bot.loop)
        except: pass # incase the message was deleted or something so it wont fuck up the whole queue
        if playlist[server][0] != []:
            if not looping[server]:
                playlist[server][0].pop(0)
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
                playlist[server] = [[],[]]
                looping[server] = False
        await ctx.message.add_reaction('👌')
        self.play_song(ctx, songs)


    @commands.command()
    async def list(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        if not server in playlist:
            return
        embed = create_embed(ctx, 0)
        message = await ctx.send(embed=embed)
        await message.edit(view=music_view(ctx=await self.bot.get_context(message), youtube=self.youtube))
        
    @commands.command()
    async def link(ctx):
        server = get_server(ctx)
        linked_message = await ctx.send("Currently playing " + str(playlist[server][0][0].title + "\n" + f"https://www.youtube.com/watch?v={playlist[server][0][0].id}"),delete_after=30)
    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        playlist[server] = [[],[]]
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
        amount = abs(int(amount))
        for _ in range(1, amount): 
            if playlist[server][0] != []:
                playlist[server][0].pop(0)
            elif playlist[server][1] != []:
                playlist[server][1].pop(0)
            else:
                break
        append_songs(ctx)
        await VoiceChat.stop(ctx) # skips one song
        await asyncio.sleep(0.5) #why? # just incase
        # also why do we not refresh the list after this. todo # done ;)
        looping[server] = temp
        await ctx.message.add_reaction('👌')
    
    @commands.command()
    async def shuffle(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        if playlist[server] == [[],[]]: return
        temp = playlist[server][0][0]
        playlist[server][0].pop(0)
        np.random.shuffle(playlist[server][0])
        np.random.shuffle(playlist[server][1])
        playlist[server][0].insert(0, temp)
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

    @commands.command()
    async def replay(self, ctx):
        if ctx.voice_client == None: return
        server = get_server(ctx)
        playlist[server][0].insert(0, playlist[server][0][0])
        await VoiceChat.stop(ctx)

class music_view(discord.ui.View):
    def __init__(self, ctx, youtube):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.youtube = youtube
        self.embed = None
        self.index = 0
        self.server = get_server(ctx)
        self.children[0].options = create_options(ctx)
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
        self.children[0].options = create_options(self.ctx)
        playlist_length = math.ceil(len(playlist[self.server][0]) / 50)

        for i in range(0, len(self.children)):
            self.children[i].disabled = False

        if self.index == 0: # no more to go back
            self.children[1].disabled = True # super back
            self.children[2].disabled = True # back
        if self.index >= playlist_length - 1: # no more to forward
            self.children[4].disabled = True # for
            self.children[5].disabled = True # super for
        if playlist[self.server][0] == []: # if the entire list is empty
            for i in range(0, len(self.children)):
                self.children[i].disabled = True
            self.children[3].disabled = False # refresh
            self.index = 0

    def update_embed(self):
        for _ in range(0, self.index + 1):
            self.embed = create_embed(self.ctx, self.index)
            if self.embed.description != '': break
            self.index -= 1
        
    @discord.ui.select(placeholder='Choose page...', min_values=0, row=0)
    async def select_callback(self, select, interaction):
        if self.ctx.voice_client == None: return
        value = int(select.values[0])
        self.index = value
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='FIRST PAGE' ,emoji='⏪', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def super_backward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index = 0
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='PREVIOUS PAGE' ,emoji='◀️', style=discord.ButtonStyle.red, row=1, disabled=True)
    async def backward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index -= 1
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='REFRESH' ,emoji='🔄', style=discord.ButtonStyle.red, row=1)
    async def refresh_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='NEXT PAGE' ,emoji='▶️', style=discord.ButtonStyle.red, row=1)
    async def forward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index += 1
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LAST PAGE' ,emoji='⏩', style=discord.ButtonStyle.red, row=1)
    async def super_forward_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        self.index = math.ceil(len(playlist[self.server]) / 50) - 1
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SKIP' ,emoji='⏭️', style=discord.ButtonStyle.red, row=2)
    async def skip_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        temp = looping[self.server]
        looping[self.server] = False
        await VoiceChat.stop(self.ctx)
        await asyncio.sleep(0.5)
        looping[self.server] = temp
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='SHUFFLE' ,emoji='🔀', style=discord.ButtonStyle.red, row=2)
    async def shuffle_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        if playlist[self.server][0] == []: return
        temp = playlist[self.server][0][0]
        playlist[self.server][0].pop(0)
        np.random.shuffle(playlist[self.server][0])
        np.random.shuffle(playlist[self.server][1])
        playlist[self.server][0].insert(0, temp)
        self.update_embed()
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='LOOP' ,emoji='🔁', style=discord.ButtonStyle.red, row=2)
    async def loop_callback(self, button, interaction):
        if self.ctx.voice_client == None: return
        looping[self.server] = not looping[self.server]
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