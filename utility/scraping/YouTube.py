from asyncio import AbstractEventLoop
import asyncio
import functools
import json
import yt_dlp
import urllib
import urllib.parse
from utility.common.requests import get_redirect_url
import validators
from utility.common.errors import UrlInvalid, VideoTooLong, VideoSearchNotFound, VideoUnavailable, YoutubeApiError
import httpx
import re
import concurrent.futures
from utility.common.config import string
from utility.common import decorators
from dataclasses import dataclass, field
import functools
import pyyoutube as YouTubePy # ugly name



zws = string.zero_width_space

@dataclass(frozen=True)
class Video:
    """
        A dataclass for the YouTube video info
    """
    id: str = field(default=None, repr=False, compare=True)
    title: str = field(default=None, repr=True, compare=False)
    channel: str = field(default=None, repr=True, compare=False)
    description: str = field(default=None, repr=False, compare=False)
    channel_id: str = field(default=None, repr=False, compare=False)
    thumbnail: str = field(default=None, repr=False, compare=False)
    localized: bool = field(default=None, repr=False, compare=False)


def _parse_data(video: YouTubePy.Video | YouTubePy.PlaylistItem, video_id: str) -> Video:
    """
        Parses the data from the results
    """
    snippet = video.snippet
    
    if isinstance(video, YouTubePy.PlaylistItem):
        title = snippet.title
        description = snippet.description
        channelId = snippet.videoOwnerChannelId
        channelTitle = snippet.videoOwnerChannelTitle
    else:
        title = snippet.localized.title
        description = snippet.localized.description
        channelId = snippet.channelId
        channelTitle = snippet.channelTitle
    
    thumbnails = snippet.thumbnails
    thumbnail = thumbnails.maxres if thumbnails.maxres else thumbnails.high
    thumbnail = thumbnail.url if thumbnail else f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg'
        
    parsed = {
        'title': title,
        'description': description,
        'channel_id': channelId,
        'channel': channelTitle,
        'id': video_id,
        'thumbnail': thumbnail,
        'localized': isinstance(video, YouTubePy.Video)
    }

    return Video(**parsed)

class YT_Extractor:
    """
        Extractor for extracting data from YouTube
    """
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str=None) -> None:
        self.loop = loop
        self.youtube = YouTubePy.Api(api_key=yt_api_key) if yt_api_key else None
        self.channel_icons = {}
        self.client = httpx.AsyncClient()

    async def get_raw_url(self, url: str, video: bool = False, max_duration: int = None):
        """
            Gets the raw url of the video / audio from YouTube
        """
        info = await self.get_info(url=url, video=video, max_duration=max_duration)
        return info['url']
    
    #@decorators.Async.logging.log
    async def get_info(self, url: str = None, id: str = None, video: bool = False, max_duration: int = None) -> dict:
        """
            Gets the info from the YouTube video
        """
        if id != None:
            url = f'https://www.youtube.com/watch?v={id}'
        if not validators.url(url):
            raise UrlInvalid()
        ydl_opts = {
            'format': 'bestaudio/best',
            'throttled-rate': '180K',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
        }
        if video:
            ydl_opts['format'] = 'best'
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            info = await self.loop.run_in_executor(
                pool, functools.partial(
                    ydl.extract_info, url,
                    download=False
                )
            )
        info['url'] = await get_redirect_url(info['url'])
        
        max_duration = info['duration'] if max_duration == None else max_duration
        if info['duration'] > max_duration:
            raise VideoTooLong(max_duration)
        return info

    
    @staticmethod
    def __get_results(ytInitialData: dict) -> dict:
        """
            Gets the results from the search
        """
        results = ytInitialData['contents']['twoColumnSearchResultsRenderer']
        results = results['primaryContents']['sectionListRenderer']  
        results = results['contents'][0]
        results = results['itemSectionRenderer']['contents']
        return results
    
    @staticmethod
    def __get_initial_data(content: str) -> dict:
        """
            Gets the initial data from a js variable in the document
        """
        # gets the variable that contains the search results
        ytInitialData = re.findall('var ytInitialData = .*};', content)
        # removes the variable declaration itself
        ytInitialData: str = ytInitialData[0][20:]
        # trims the end of any gunk that would otherwise run the conversion
        ytInitialData = ytInitialData.split('};')[0] + '}'
        # str -> dict
        ytInitialData = json.loads(ytInitialData)  

        return ytInitialData

    # youtube api searches are expensive so webscraping it is
    #@decorators.Async.logging.log
    async def fetch_from_search(self, query: str) -> Video:
        """
            Scrapes the Youtube search results page for videos
        """
        urlsafe_quote = urllib.parse.quote(query)
        url = 'https://www.youtube.com/results?search_query=' + urlsafe_quote
        resp = await self.client.get(url)
        resp.raise_for_status()
        content = resp.content.decode()
        try:    
            ytInitialData = self.__get_initial_data(content)
            results = self.__get_results(ytInitialData) # the videos
            for result in [result for result in results if 'videoRenderer' in result]:
                videoId = result['videoRenderer']['videoId']
                result = await self.fetch_from_video(videoId)
                return result
            raise VideoSearchNotFound(query)
        except VideoSearchNotFound:
            raise VideoSearchNotFound(query)

    #@decorators.Async.logging.log
    async def fetch_from_video(self, video_id: str) -> list[Video]:
        """
            Fetches the data from a video
        """
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                video = await self.loop.run_in_executor(
                    pool, functools.partial(
                        self.youtube.get_video_by_id,
                        video_id=video_id,
                        parts='snippet'
                    )
                )
        except:
            raise YoutubeApiError()
        if not video.items:
            raise YoutubeApiError()
        result = _parse_data(
            video=video.items[0],
            video_id=video_id
        )
        return result


    ##@decorators.Async.logging.log
    async def fetch_from_playlist(self, playlist_id: str) -> list[Video]:
        """
            Fetches the data from a playlist
        """
        pool = concurrent.futures.ThreadPoolExecutor()
        condition = True
        next_page_token = None
        while condition:
            try:
                playlist = await self.loop.run_in_executor(
                    pool, functools.partial(
                        self.youtube.get_playlist_items,
                        playlist_id=playlist_id,
                        page_token=next_page_token,
                        parts='snippet',
                        count=50,
                        limit=50
                    )
                )
                next_page_token = playlist.nextPageToken
                items: list[YouTubePy.PlaylistItem] = playlist.items
                videos = [
                    _parse_data(
                        video=item,
                        video_id=item.snippet.resourceId.videoId,
                    ) for item in items
                ]
                condition = next_page_token is not None
                yield videos
            except:
                raise YoutubeApiError()
    
    #@decorators.Async.logging.log
    async def fetch_channel_icon(self, channel_id: str) -> str:
        """
            Fetches the channel icon 
        """
        key = channel_id
        if key in self.channel_icons:
            return self.channel_icons[key]
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                channel = await self.loop.run_in_executor(
                    pool, functools.partial(
                        self.youtube.get_channel_info,
                        channel_id=channel_id,
                        parts='snippet'
                    )
                ) 
        except:
            raise YoutubeApiError()
        
        icon = channel.items[0].snippet.thumbnails.default.url
        self.channel_icons[key] = icon
        
        return icon

async def get_raw_url(url, format='best'):
    """
        Gets the raw url to a YouTube video
    """
    loop = asyncio.get_running_loop()
    
    ydl_opts = {
       'format': format,
       'restrictfilenames': True,
       'noplaylist': True,
       'nocheckcertificate': True,
       'ignoreerrors': False,
       'logtostderr': False,
       'quiet': True,
       'no_warnings': True,
       'default_search': 'auto'
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    with concurrent.futures.ThreadPoolExecutor() as pool:
        info = await loop.run_in_executor(
            pool,
            functools.partial(
                ydl.extract_info, url,
                download=False
            )
        )
    raw_url = info['url']
    raw_url = await get_redirect_url(raw_url)
    return raw_url