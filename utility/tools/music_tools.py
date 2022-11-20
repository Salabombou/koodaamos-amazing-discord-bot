from utility.scraping import YouTube
from utility.common.errors import UrlInvalid, SongNotFound
from utility.scraping.YouTube import YT_Extractor
from utility.common.requests import get_redirect_url
from discord.ext import commands
from urllib.parse import parse_qs, urlparse
import discord
import math
import asyncio
from asyncio import AbstractEventLoop
import validators
import numpy as np
from utility.common import decorators
from utility.common import embed_config


ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}



class music_tools:
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str) -> None:
        self.loop = loop
        self.yt_extractor = YT_Extractor(loop, yt_api_key)
        self.playlist: dict[list[list, list]] = {}
        self.looping = {}
        self.link_values = lambda song: f'Video:\n[{song.title}](https://www.youtube.com/watch?v={song.id})\n\nChannel:\n[{song.channel}](https://www.youtube.com/channel/{song.channelId})'
        self.yt_error_vid_id = 'J3lXjYWPoys'

    # appends songs to the playlist
    @decorators.Sync.get_server
    def append_songs(self, ctx, /, playnext=False, songs=[], *, server: str = None):
        if playnext and songs != []:
            for song in songs[::-1]:
                self.playlist[server][0].insert(1, song)
            self.playlist[server][1] += self.playlist[server][0][-len(songs):][::-1]
            del self.playlist[server][0][-len(songs):]
        else:
            self.playlist[server][1] += songs
        length = len(self.playlist[server][0])
        # limits the visible playlist to go to upto 1000 song at once
        self.playlist[server][0] += self.playlist[server][1][:1000 - length]
        del self.playlist[server][1][:1000 - length]

    def serialize_songs(self, server):
        songs = []
        for i, song in enumerate(self.playlist[server][0]):
            digit = str(i).zfill(3)
            title = song.title
            title_length = len(title)
            if title_length > 63:
                title = song.title[:63]
                title += ' ...'
            song = f'**``{digit}``**: {title}'
            songs.append(song)
        if len(songs) <= 1:
            return ['']
        songs.pop(0)
        return songs

    @decorators.Sync.get_server
    def create_embed(self, ctx: commands.Context, page_num: int, *, server: str = None):  # todo add timestamp
        embed = discord.Embed(
            title='PLAYLIST',
            description='',
            fields=[],
            color=embed_config.color
        )
        index = page_num * 50
        playlist_length = math.ceil(len(self.playlist[server][0]) / 50)
        songs = self.serialize_songs(server)
        currently_playing = YouTube.VideoDummie()
        if self.playlist[server][0] != []:
            currently_playing = self.playlist[server][0][0]
        for song in songs[index:50 + index][::-1]:
            embed.description += song + '\n'
        embed.add_field(
            name='CURRENTLY PLAYING:',
            value=f'```{currently_playing.title}```'
        )
        embed.set_footer(
            text=f'Showing song(s) in the playlist queue from page {page_num+1}/{playlist_length} out of {len(self.playlist[server][0])} song(s) in the queue'
        )  # bigggggg
        return embed
    @decorators.Sync.get_server
    def create_options(self, ctx: commands.Context | discord.Message, *, server: str = None):  # create the options for the dropdown select menu
        page_amount = math.ceil(len(self.playlist[server][0]) / 50)
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
    
    @decorators.Async.get_server
    async def create_info_embed(self, ctx: commands.Context, number=0, song: YouTube.Video = None, *, server: str = None):
        if song == None:
            num = abs(number)
            if len(self.playlist[server][0]) - 1 < num:
                raise SongNotFound()
            song = self.playlist[server][0][num]

        embed = discord.Embed(
            title=song.title,
            description=song.description,
            fields=[],
            color=embed_config.color
        )

        embed.set_image(url=song.thumbnail)
        embed.add_field(
            name='LINKS:',
            value=self.link_values(song)
        )
        icon = await self.yt_extractor.fetch_channel_icon(channelId=song.channelId)
        embed.set_footer(text=song.channel, icon_url=icon)
        return embed

    async def fetch_songs(self, ctx: commands.Context, url, no_playlists=False):
        if not validators.url(url):  # if url is invalid (implying for a search)
            # searches for the video and returns the url to it
            song = await self.yt_extractor.fetch_from_search(query=url)
            await ctx.send(f"found a video with the query '{url}' with the title '{song.title}'.", delete_after=10, mention_author=False)
            return [song]
        url = await get_redirect_url(url)
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        if 'v' in query:
            return [await self.yt_extractor.fetch_from_video(videoId=query['v'][0])]
        elif 'list' in query and not no_playlists:
            # fething from playlist takes time
            message = await ctx.send('Fetching from playlist...')
            songs = await self.yt_extractor.fetch_from_playlist(playlistId=query['list'][0])
            await message.delete()
            return songs
        raise UrlInvalid()

    def shuffle_playlist(self, server: str):
        temp = self.playlist[server][0][0]
        self.playlist[server][0].pop(0)
        np.random.shuffle(self.playlist[server][0])
        np.random.shuffle(self.playlist[server][1])
        self.playlist[server][0].insert(0, temp)

    @decorators.Async.get_server
    async def play_song(self, ctx: commands.Context, songs=[], playnext=False, next_song=False, server: str = None): # plays a song in voice chat
        if ctx.voice_client == None:
            return
        
        self.append_songs(ctx, songs=songs, playnext=playnext)
        
        await asyncio.sleep(1)
       
        if ctx.voice_client.is_playing() and not next_song:
            return
        
        if next_song and ctx.voice_client.is_playing():
            return await self.play_song(ctx, playnext, songs, next_song=next_song)
        
        
        
        if self.playlist[server][0] == []:
            return
            
        song: YouTube.Video = self.playlist[server][0][0]

        try:
            info = await self.yt_extractor.get_info(id=song.id)
        except:
            info = await self.yt_extractor.get_info(id=self.yt_error_vid_id)

        source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
        embed = await self.create_info_embed(ctx)
        message = await ctx.send('Now playing:', embed=embed)

        ctx.voice_client.play(
            discord.PCMVolumeTransformer(
                source,
                volume=0.75
            ),
            after=lambda _: self.next_song(ctx, message)
        )
    @decorators.Sync.get_server
    def next_song(self, ctx: commands.Context, message: discord.Message, *, server: str = None):
        try:
            asyncio.run_coroutine_threadsafe(
                message.delete(),
                self.loop
            )
        except:
            pass  # incase the message was already deleted or something so it wont fuck up the whole queue
        self.append_songs(ctx)

        if self.playlist[server][0] == []:
            return

        if self.looping[server]: # if looping is enabled (moves the current song to the end of the playlist)
            self.playlist[server][1].append(self.playlist[server][0][0]) # adds the currently playing song to the end of the playlist
        self.playlist[server][0].pop(0)
        asyncio.run_coroutine_threadsafe(
            self.play_song(ctx, next_song=True),
            self.loop
        )
    @decorators.Async.get_server
    async def looping_response(self, ctx: commands.Context, *, server: str = None) -> discord.Message:
        return await ctx.send('LOOPING' if self.looping[server] else 'NOT LOOPING', delete_after=10)