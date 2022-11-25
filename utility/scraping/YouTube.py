from asyncio import AbstractEventLoop
import asyncio
import functools
import googleapiclient.discovery
import json
import yt_dlp
import urllib
import urllib.parse
from urllib.parse import urlparse, parse_qs
from utility.common.requests import get_redirect_url
import validators
from utility.common.errors import UrlInvalid, VideoTooLong, VideoSearchNotFound, VideoUnavailable, YoutubeApiError
import httpx
import re
import concurrent.futures
from utility.common.config import string
from utility.common import decorators

zws = string.zero_width_space

class VideoDummie:
    """
        A dummie version used as a placeholder
    """
    title = zws
    description = zws
    channel = zws
    id = zws
    thumbnail = f'https://i.ytimg.com/vi/{id}/mqdefault.jpg'
    channelId = zws
    other = zws

class Video:
    """
        A class object for the YouTube video info
    """
    def __init__(
        self, /,
        title: str,
        description: str,
        channelId: str,
        channelTitle: str,
        videoId: str,
        thumbnail: str,
        **kwargs
    ) -> None:
        self.title = title
        self.description = description
        self.channel = channelTitle
        self.id = videoId
        self.thumbnail = thumbnail
        self.channelId = channelId
        self.other = kwargs


def _parse_data(data: dict, videoId, from_playlist: bool) -> Video:
    """
        Parses the data from the results
    """
    snippet = data['snippet']
    
    channelId = snippet['channelId']
    channelTitle = snippet['channelTitle']
    
    if not from_playlist:
        pass
    elif'videoOwnerChannelId' in snippet and 'videoOwnerChannelTitle' in snippet:
        channelId = snippet['videoOwnerChannelId']
        channelTitle = snippet['videoOwnerChannelTitle']
    
    thumbnails = snippet['thumbnails']
    thumbnail_key = 'maxres' if 'maxres' in thumbnails else 'high'
    
    if thumbnail_key in thumbnails:
        thumbnail = thumbnails[thumbnail_key]['url']
    else:
        thumbnail = f'https://i.ytimg.com/vi/{videoId}/mqdefault.jpg'
        
    parsed = {
        'title': snippet['title'],
        'description': snippet['description'],
        'channelId': channelId,
        'channelTitle': channelTitle,
        'videoId': videoId,
        'thumbnail': thumbnail
    }

    return Video(**parsed)

class YT_Extractor:
    """
        Extractor for extracting data from YouTube
    """
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str=None) -> None:
        self.loop = loop
        self.youtube = None
        if not yt_api_key is None:
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', developerKey=yt_api_key
            )
        self.channel_icons = {}
        self.client = httpx.AsyncClient()

    async def get_raw_url(self, url: str, video: bool = False, max_duration: int = None):
        """
            Gets the raw url of the video / audio from YouTube
        """
        info = await self.get_info(url=url, video=video, max_duration=max_duration)
        return info['url']
    
    @decorators.Async.logging.log
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
    @decorators.Async.logging.log
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

    @decorators.Async.logging.log
    async def fetch_from_video(self, videoId: str) -> list[Video]:
        """
            Fetches the data from a video
        """
        request = self.youtube.videos().list(
            part='snippet',
            id=videoId
        )
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                r = await self.loop.run_in_executor(
                    pool, request.execute
                )
        except:
            raise YoutubeApiError()
        if r['items'] != []:
            result = _parse_data(
                data=r['items'][0],
                videoId=videoId,
                from_playlist=False
            )
            return result
        else:
            raise VideoUnavailable()


    @decorators.Async.logging.log
    async def fetch_from_playlist(self, playlistId: str) -> list[Video]:
        """
            Fetches the data from a playlist
        """
        request = self.youtube.playlistItems().list(
            part='snippet',
            playlistId=playlistId,
            maxResults=1000
        )
        items = []
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                while request != None:
                    r = await self.loop.run_in_executor(
                        pool, request.execute
                    )
                    items += r['items']
                    request = self.youtube.playlistItems().list_next(request, r)
        except:
            raise YoutubeApiError()
        songs = [
            _parse_data(
                data=song,
                videoId=song['snippet']['resourceId']['videoId'],
                from_playlist=True
            ) for song in items
        ]
        return songs
    
    
    @decorators.Async.logging.log
    async def fetch_channel_icon(self, channelId: str) -> str:
        """
            Fetches the channel icon 
        """
        key = channelId
        if key in self.channel_icons:
            return self.channel_icons[key]
        
        request = self.youtube.channels().list(
            part='snippet',
            id=channelId
        )
        try:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                r = await self.loop.run_in_executor(
                    pool, request.execute
                )
        except:
            raise YoutubeApiError()
        icon = r['items'][0]['snippet']['thumbnails']['default']['url']
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