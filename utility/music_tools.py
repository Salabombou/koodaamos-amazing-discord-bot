from utility import common, YouTube
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

class decorators:
    def update_playlist(func):
        @functools.wraps(func)
        async def wrapper(*args):
            self = args[0]
            ctx = args[1]
            server = common.get_server(ctx)
            if server not in self.playlist:
                self.playlist[server] = [[],[]]
            if server not in self.looping:
                self.looping[server] = False
            return await func(*args)
        return wrapper

def append_songs(ctx, playlist, songs=[]): # appends songs to the playlist
    server = common.get_server(ctx)
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

def serialize_songs(playlist, server):
    i = 0
    songs = []
    for song in playlist[server][0]:
        digit = str(i).zfill(3)
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

def create_embed(ctx, playlist, page_num): # todo add timestamp
    server = common.get_server(ctx)
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
    server = common.get_server(ctx)
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
    server = common.get_server(ctx)
    if song == None:
        song = self.playlist[server][0][abs(int(number))]
    embed = discord.Embed(title=song.title, description=song.description, fields=[], color=0xC4FFBD)
    embed.set_image(url=song.thumbnail)
    embed.add_field(name='LINKS:', value=f'\n\n`  Video:` [{song.title}](https://www.youtube.com/watch?v={song.id})\n`Channel:` [{song.channel}](https://www.youtube.com/channel/{song.channelId})')
    icon = YouTube.fetch_channel_icon(youtube=self.youtube, channelId=song.channelId)
    embed.set_footer(text=song.channel, icon_url=icon)
    return embed

async def fetch_songs(self, ctx, url, args):        # todo get first song in list and play it, after that get rest
    if args != () or not validators.url(url): # if there are more than 1 arguement or the url is invalid (implying for a search)
        search_query = f"{url} {' '.join(args)}"
        song = YouTube.fetch_from_search(self.youtube, query=search_query)[0] # searches for the video and returns the url to it
        await ctx.reply(f"found a video with the query '{search_query}' with the title '{song.title}'.", delete_after=10, mention_author=False)
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
            append_songs(ctx, self.playlist, songs)
        asyncio.ensure_future(fetch_the_rest()) # fire and forget
        return [song]
    raise Exception('Invalid url')

def play_song(self, ctx, songs=[]):
    if ctx.voice_client == None:
        return
    server = common.get_server(ctx)
    append_songs(ctx, self.playlist, songs)
    if not ctx.voice_client.is_playing() and self.playlist[server][0] != []:
        song = self.playlist[server][0][0]
        url = YouTube.get_raw_audio_url(f'https://www.youtube.com/watch?v={song.id}')
        source = discord.FFmpegPCMAudio(url, **ffmpeg_options)
        embed = create_info_embed(self, ctx)
        message = asyncio.run_coroutine_threadsafe(ctx.send('Now playing:', embed=embed), self.bot.loop)
        ctx.voice_client.play(discord.PCMVolumeTransformer(source, volume=0.5), after=lambda e: next_song(self, ctx, message._result))

def next_song(self, ctx, message):
    server = common.get_server(ctx)
    try:
        asyncio.run_coroutine_threadsafe(message.delete(), self.bot.loop)
    except: pass # incase the message was deleted or something so it wont fuck up the whole queue
    if self.playlist[server][0] != []:
        if not self.looping[server]:
            self.playlist[server][0].pop(0)
        play_song(self, ctx)    