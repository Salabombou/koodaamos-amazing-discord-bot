
from discord.ext import commands, bridge
import discord
from urllib.parse import parse_qs, urlparse
from asyncio import AbstractEventLoop
import numpy as np
import validators
import asyncio
import math

from utility.common import decorators, config
from utility.ui.views.music import song_view
from utility.scraping import YouTube
from utility.common.errors import UrlInvalid, SongNotFound
from utility.scraping.YouTube import YT_Extractor
from utility.common.requests import get_redirect_url


ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}


class music_tools:
    def __init__(self, bot: commands.Bot, loop: AbstractEventLoop, yt_api_key: str) -> None:
        self.bot = bot
        self.loop = loop
        self.yt_extractor = YT_Extractor(loop, yt_api_key)
        self.playlist: dict[list[list, list]] = {}
        self.looping = {}
        self.voice_client = {}

    # appends songs to the playlist
    def append_songs(self, ctx: bridge.BridgeExtContext, /, playnext=False, songs=[]):
        if playnext and songs != []:
            for song in songs[::-1]:
                self.playlist[ctx.guild.id][0].insert(1, song)
            self.playlist[ctx.guild.id][1] += self.playlist[ctx.guild.id][0][-len(songs):][::-1]
            del self.playlist[ctx.guild.id][0][-len(songs):]
        else:
            self.playlist[ctx.guild.id][1] += songs
            
        length = len(self.playlist[ctx.guild.id][0])
        
        # limits the visible playlist to go to upto 1000 song at once
        self.playlist[ctx.guild.id][0] += self.playlist[ctx.guild.id][1][:1000 - length]
        del self.playlist[ctx.guild.id][1][:1000 - length]
        
    def serialize_songs(self, ID):
        songs = []
        for i, song in enumerate(self.playlist[ID][0]):
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
    
    def create_embed(self, ctx: bridge.BridgeExtContext, page_num: int):  # todo add timestamp
        embed = discord.Embed(
            title='PLAYLIST',
            description='',
            fields=[],
            color=config.embed.color
        )
        index = page_num * 50
        playlist_length = math.ceil(len(self.playlist[ctx.guild.id][0]) / 50)
        songs = self.serialize_songs(ctx.guild.id)
        currently_playing = YouTube.Video()
        if self.playlist[ctx.guild.id][0] != []:
            currently_playing = self.playlist[ctx.guild.id][0][0]
        for song in songs[index:50 + index][::-1]:
            embed.description += song + '\n'
        embed.add_field(
            name='CURRENTLY PLAYING:',
            value=f'```{currently_playing.title or config.string.zero_width_space}```'
        )
        embed.set_footer(
            text=f'Showing song(s) in the playlist queue from page {page_num+1}/{playlist_length} out of {len(self.playlist[ctx.guild.id][0])} song(s) in the queue'
        )  # bigggggg
        return embed

    def create_options(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext | discord.Message):  # create the options for the dropdown select menu
        page_amount = math.ceil(len(self.playlist[ctx.guild.id][0]) / 50)
        options = [
            discord.SelectOption(
                label='Page 1',
                description='',
                value='0'
            )
        ]
        for i in range(1, page_amount):
            options.append(
                discord.SelectOption(
                    label=f'Page {i+1}',
                    description='',
                    value=str(i)
                )
            )
        return options
    
    async def create_info_embed(self, ctx: bridge.BridgeExtContext, number=0, song: YouTube.Video = None) -> tuple[discord.Embed, discord.ui.View]:
        if song == None:
            num = abs(number)
            if len(self.playlist[ctx.guild.id][0]) - 1 < num:
                raise SongNotFound()
            song = self.playlist[ctx.guild.id][0][num]

        embed = discord.Embed(
            title=song.title,
            description=song.description,
            fields=[],
            color=config.embed.color
        )

        embed.set_image(url=song.thumbnail)
        try:
            icon = await self.yt_extractor.fetch_channel_icon(channelId=song.channelId)
        except:
            icon = song.thumbnail
        embed.set_footer(text=song.channelTitle, icon_url=icon)
        view = song_view(song)
        return embed, view
    
    async def append_songs_from_playlist(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, playlist):
        await asyncio.sleep(3) # just incase
        async for batch in playlist:
            self.append_songs(ctx, songs=batch)
    
    #@decorators.Async.logging.log
    async def fetch_songs(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, url, no_playlists=False):
        if not validators.url(url):  # if url is invalid (implying for a search)
            # searches for the video and returns the url to it
            song = await self.yt_extractor.fetch_from_search(query=url)
            await ctx.channel.send(f"found a video with the query '{url}' with the title '{song.title}'.", delete_after=10)
            return [song]
        url = await get_redirect_url(url)
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        if 'v' in query:
            return [await self.yt_extractor.fetch_from_video(videoId=query['v'][0])]
        elif 'list' in query and not no_playlists:
            playlist = self.yt_extractor.fetch_from_playlist(playlistId=query['list'][0])
            return_value = await anext(playlist)
            asyncio.run_coroutine_threadsafe(
                self.append_songs_from_playlist(ctx, playlist),
                self.loop
            )
            return return_value
        raise UrlInvalid()

    def shuffle_playlist(self, ID: int):
        temp = self.playlist[ID][0][0]
        self.playlist[ID][0].pop(0)
        np.random.shuffle(self.playlist[ID][0])
        np.random.shuffle(self.playlist[ID][1])
        self.playlist[ID][0].insert(0, temp)

    
    async def send_song_unavailable(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, next_song: bool):
        try:
            message = await ctx.channel.send('Song unavailable, moving to next one')
            self.playlist[ctx.guild.id][0].pop(0)
            await self.play_song(ctx, next_song=next_song)
            return await message.delete(delay=1)
        except:
            return
    
    # making sure this wont ever raise an exception and thus stop the music from playing
    #@decorators.Async.logging.log
    async def play_song(self, ctx: bridge.BridgeExtContext, songs=[], playnext=False, next_song=False):
        """
            Song player handler
        """
        if ctx.voice_client == None:
            return
        
        self.append_songs(ctx, songs=songs, playnext=playnext)
        
        await asyncio.sleep(0.2)
       
        if ctx.voice_client.is_playing() and not next_song:
            return
        
        if next_song and ctx.voice_client.is_playing():
            return await self.play_song(ctx, next_song=True)
        
        if self.playlist[ctx.guild.id][0] == []:
            return
            
        song: YouTube.Video = self.playlist[ctx.guild.id][0][0]

        try:
            info = await self.yt_extractor.get_info(id=song.id)
        except:
            return await self.send_song_unavailable(ctx, next_song)

        source = discord.FFmpegPCMAudio(info['url'], **ffmpeg_options)
        
        try:
            embed, view = await self.create_info_embed(ctx)
            message = await ctx.channel.send('Now playing:', embed=embed, view=view)
        except:
            message = None
        
        ctx.voice_client.play(
            discord.PCMVolumeTransformer(
                source,
                volume=0.5
            ),
            after=lambda _: self.next_song(ctx, message)
        )
        

    def next_song(self, ctx: bridge.BridgeExtContext, message: discord.Message):
        """
            Function to be called after song id done playing from play_song
        """
        try:
            asyncio.run_coroutine_threadsafe(
                message.delete(),
                self.loop
            )
        except:
            pass  # incase the message was already deleted or something so it wont fuck up the whole queue
        
        self.append_songs(ctx)
        
        if self.playlist[ctx.guild.id][0] == []:
            return
        
        if self.looping[ctx.guild.id]: # if looping is enabled (moves the current song to the end of the playlist)
            self.playlist[ctx.guild.id][1].append(self.playlist[ctx.guild.id][0][0]) # adds the currently playing song to the end of the playlist
        self.playlist[ctx.guild.id][0].pop(0)
        asyncio.run_coroutine_threadsafe(
            self.play_song(ctx, next_song=True),
            self.loop
        )
    
    #@decorators.Async.logging.log
    async def looping_response(self, ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext) -> discord.Message:
        return await ctx.channel.send('LOOPING' if self.looping[ctx.guild.id] else 'NOT LOOPING', delete_after=10)