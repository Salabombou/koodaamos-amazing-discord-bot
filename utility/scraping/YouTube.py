from asyncio import AbstractEventLoop
import asyncio
import functools
import yt_dlp
from utility.common.requests import get_redirect_url
import validators
from utility.common.errors import UrlInvalid, VideoTooLong, VideoSearchNotFound, YoutubeApiError
import httpx
import concurrent.futures
from utility.common.config import string
from dataclasses import dataclass, field
import functools
import pyyoutube as YouTubePy # ugly name
from typing import Any


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


def _parse_data(video: YouTubePy.PlaylistItem | dict[str, Any], video_id: str) -> Video:
    """
        Parses the data from the results
    """
    kwargs = {
        'id': video_id
    }
    if isinstance(video, dict):
        kwargs = {
            **kwargs,
            'title': video['title'],
            'channel': video['uploader'],
            'description': video['description'],
            'channel_id': video['channel_id'],
            'thumbnail': video['thumbnail'],  
        }
    else:
        snippet = video.snippet
    
        title = snippet.title
        description = snippet.description
        channelId = snippet.videoOwnerChannelId
        channelTitle = snippet.videoOwnerChannelTitle
    
        thumbnails = snippet.thumbnails
        thumbnail = thumbnails.maxres if thumbnails.maxres else thumbnails.high
        thumbnail = thumbnail.url if thumbnail else f'https://i.ytimg.com/vi/{video_id}/mqdefault.jpg'
        
        kwargs = {
            **kwargs,
            'title': title,
            'channel': channelTitle,
            'description': description,
            'channel_id': channelId,
            'thumbnail': thumbnail
        }
    return Video(**kwargs)

class YT_Extractor:
    """
        Extractor for extracting data from YouTube
    """
    ydl_opts = {
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto'
    }
    
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str=None) -> None:
        self.loop = loop
        self.youtube = YouTubePy.Api(api_key=yt_api_key) if yt_api_key else None
        self.channel_icons = {}
        self.client = httpx.AsyncClient()
        self.ydl = yt_dlp.YoutubeDL(self.ydl_opts)

    async def get_raw_url(self, url: str = None, id: str = None, video: bool = False, max_duration: int = None):
        """
            Gets the raw url of the video / audio from YouTube
        """
        info = await self.get_info(url=url, id=id, video=video, max_duration=max_duration)
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
            **self.ydl_opts,
            'format': 'bestaudio/best' if not video else 'best'
        }
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

    #@decorators.Async.logging.log
    async def fetch_from_search(self, query: str) -> Video:
        """
            Scrapes the Youtube search results page for videos
        """
        with concurrent.futures.ThreadPoolExecutor() as pool:
            search_results = await self.loop.run_in_executor(
                pool, functools.partial(
                    self.ydl.extract_info,
                    url=f'ytsearch:\'{query}\'',
                    download=False
                )
            )
        search_results = search_results['entries']
        if not search_results:
            raise VideoSearchNotFound(query)
        
        video = search_results[0]
        return _parse_data(video, video_id=video['id'])

    #@decorators.Async.logging.log
    async def fetch_from_video(self, video_id: str) -> list[Video]:
        """
            Fetches the data from a video
        """
        url = 'https://www.youtube.com/watch?v=' + video_id
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                video = await self.loop.run_in_executor(
                    pool, functools.partial(
                        self.ydl.extract_info,
                        url,
                        download=False
                    )
                )
        except:
            raise YoutubeApiError()
        return _parse_data(video, video_id=video_id)


    ##@decorators.Async.logging.log
    async def fetch_from_playlist(self, playlist_id: str) -> list[Video]:
        """
            Fetches the data from a playlist
        """
        condition = True
        page_token = None
        while condition:
            try:
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    playlist = await self.loop.run_in_executor(
                        pool, functools.partial(
                            self.youtube.get_playlist_items,
                            playlist_id=playlist_id,
                            page_token=page_token,
                            parts='snippet',
                            count=50,
                            limit=50
                        )
                    )
                items: list[YouTubePy.PlaylistItem] = playlist.items
                videos = [
                    _parse_data(
                        video=item,
                        video_id=item.snippet.resourceId.videoId,
                    ) for item in items
                ]
                page_token = playlist.nextPageToken
                condition = page_token is not None
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
        **YT_Extractor.ydl_opts,
       'format': format,
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