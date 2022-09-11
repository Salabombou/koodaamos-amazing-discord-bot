from utility import YouTube
import urllib
from urllib.parse import parse_qs, urlparse
import isodate
import discord
import math
import asyncio
import validators
import functools

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

def get_server(ctx):
    return str(ctx.message.guild.id)

class decorators:
    def update_playlist(func):
        @functools.wraps(func)
        async def wrapper(*args):
            self = args[0]
            ctx = args[1]
            server = get_server(ctx)
            if not server in self.playlist:
                self.playlist[server] = [[],[]]
            if server not in self.looping:
                self.looping[server] = False
            return await func(*args)
        return wrapper

def append_songs(ctx, playlist, playnext=False, songs=[]): # appends songs to the playlist
    server = get_server(ctx)
    if playnext:
        playlist[server][0].insert(1, songs[0])
        playlist[server][1].insert(0, playlist[server][0][-1])
        del playlist[server][0][-1]
    else:
        playlist[server][1] += songs
    length = len(playlist[server][0])
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

def serialize_songs(playlist, server):
    i = 0
    songs = []
    for song in playlist[server][0]:
        digit = str(i).zfill(3)
        title = song.title[0:31]
        title_length = len(title)
        if title_length == 31 :
            title += ' ...'
        song = f'**``{digit}``**: {title}'
        songs.append(song)
        i += 1
    if len(songs) <= 1:
        return ['']
    songs.pop(0)
    return songs

def create_embed(ctx, playlist, page_num): # todo add timestamp
    server = get_server(ctx)
    embed = discord.Embed(title='PLAYLIST', description='', fields=[], color=0xC4FFBD)
    index = page_num * 50
    playlist_length = math.ceil(len(playlist[server][0]) / 50)
    songs = serialize_songs(playlist, server)
    currently_playing = YouTube.Video()
    if playlist[server][0] != []:
        currently_playing = playlist[server][0][0]
    for song in songs[index:50 + index][::-1]:
        embed.description += song + '\n'
    embed.add_field(name='CURRENTLY PLAYING:', value=f'```{currently_playing.title}```')
    embed.set_footer(text=f'Showing song(s) in the playlist queue from page {page_num+1}/{playlist_length} out of {len(playlist[server][0])} song(s) in the queue') # bigggggg
    return embed

def create_options(ctx, playlist):
    server = get_server(ctx)
    page_amount = math.ceil(len(playlist[server][0]) / 50)
    options = [
        discord.SelectOption(
            label='Page 1',
            description='',
            value='0'
            )]
    for i in range(1, page_amount):
        options.append(
            discord.SelectOption(
                label=f'Page {i+1}',
                description='',
                value=str(i)
                )
            )
    return options

def create_info_embed(self, ctx, number='0', song=None):
    server = get_server(ctx)
    if song == None:
        num = abs(int(number))
        if len(self.playlist[server][0]) - 1 < num :  
            raise Exception('No songs found at that number.')
        song = self.playlist[server][0][num]
    embed = discord.Embed(title=song.title, description=song.description, fields=[], color=0xC4FFBD)
    embed.set_image(url=song.thumbnail)
    embed.add_field(name='LINKS:', value=f'Video:\n[{song.title}](https://www.youtube.com/watch?v={song.id})\n\nChannel:\n[{song.channel}](https://www.youtube.com/channel/{song.channelId})')
    icon = YouTube.fetch_channel_icon(youtube=self.youtube, channelId=song.channelId)
    embed.set_footer(text=song.channel, icon_url=icon)
    return embed

async def fetch_songs(self, ctx, url, no_playlists=False):
    if not validators.url(url): # if url is invalid (implying for a search)
        song = YouTube.fetch_from_search(self.youtube, query=url)[0] # searches for the video and returns the url to it
        await ctx.reply(f"found a video with the query '{url}' with the title '{song.title}'.", delete_after=10, mention_author=False)
        return [song]
    r = urllib.request.urlopen(url)
    url = r.url
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    if 'v' in query:
        return YouTube.fetch_from_video(self.youtube, videoId=query['v'][0])
    elif 'list' in query and not no_playlists:
        songs = await YouTube.fetch_from_playlist(ctx, self.youtube, playlistId=query['list'][0])
        return songs
    raise Exception('Invalid url')

def play_song(self, ctx, songs=[], playnext=False):
    if ctx.voice_client == None:
        return
    server = get_server(ctx)
    append_songs(ctx, self.playlist, playnext, songs)
    if not ctx.voice_client.is_playing() and self.playlist[server][0] != []:
        song = self.playlist[server][0][0]
        try:
            info = YouTube.get_info('https://www.youtube.com/watch?v=' + song.id)
        except: info = YouTube.get_info('https://www.youtube.com/watch?v=J3lXjYWPoys')
        duration = None
        if 'duration' in info:
            duration = info['duration'] + 10
        source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
        embed = create_info_embed(self, ctx)
        message = asyncio.run_coroutine_threadsafe(ctx.send('Now playing:', embed=embed, delete_after=duration), self.bot.loop)
        ctx.voice_client.play(discord.PCMVolumeTransformer(source, volume=0.8), after=lambda e: next_song(self, ctx, message._result))

def next_song(self, ctx, message):
    server = get_server(ctx)
    try:
        asyncio.run_coroutine_threadsafe(message.delete(), self.bot.loop)
    except: pass # incase the message was already deleted or something so it wont fuck up the whole queue
    if self.playlist[server][0] != []:
        if not self.looping[server]:
            self.playlist[server][0].pop(0)
        play_song(self, ctx)