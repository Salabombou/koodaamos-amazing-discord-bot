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
from utility.common.errors import UrlInvalid, VideoTooLong, VideoSearchNotFound, VideoUnavailable
import httpx
import re
import concurrent.futures
from utility.common.string import zero_width_space as zws

class VideoDummie: # dummie version used as a placeholder
    def __init__(self) -> None:
        self.title = zws
        self.description = zws
        self.channel = zws
        self.id = zws
        self.thumbnail = f'https://i.ytimg.com/vi/{self.id}/mqdefault.jpg'
        self.channelId = zws
        self.other = zws

class Video:  # for the video info
    def __init__(
        self, /,
        title: str,
        description: str,
        channelId: str,
        channelTitle: str,
        videoId,
        **kwargs
    ) -> None:
        self.title = title
        self.description = description
        self.channel = channelTitle
        self.id = videoId
        self.thumbnail = f'https://i.ytimg.com/vi/{self.id}/mqdefault.jpg'
        self.channelId = channelId
        self.other = kwargs


def _parse_data(data: dict, videoId, from_playlist: bool) -> Video:
    snippet = data['snippet']
    
    channelId = snippet['channelId']
    channelTitle = snippet['channelTitle']
    try:
        if from_playlist:
            channelId = snippet['videoOwnerChannelId']
            channelTitle = snippet['videoOwnerChannelTitle']
    except KeyError:
        channelTitle = '???'

    parsed = {
        'title': snippet['title'],
        'description': snippet['description'],
        'channelId': channelId,
        'channelTitle': channelTitle,
        'videoId': videoId,
    }

    return Video(**parsed)

class YT_Extractor:
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str=None) -> None:
        self.loop = loop
        self.youtube = None
        if not yt_api_key is None:
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', developerKey=yt_api_key
            )
        self.client = httpx.AsyncClient()

    async def get_raw_url(self, url: str, video: bool = False, max_duration: int = None):
        info = await self.get_info(url=url, video=video, max_duration=max_duration)
        return info['url']

    async def get_info(self, url: str = None, id: str = None, video: bool = False, max_duration: int = None) -> dict:
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                info = await self.loop.run_in_executor(
                    pool, functools.partial(
                        ydl.extract_info, url,
                        download=False
                    )
                )
            info['url'] = await get_redirect_url(info['url'])
            if max_duration != None:
                if info['duration'] < max_duration:
                    return info
            else:
                return info
            raise VideoTooLong(max_duration)
    
    @staticmethod
    def __get_results(ytInitialData: dict) -> dict:
        results = ytInitialData['contents']['twoColumnSearchResultsRenderer']
        results = results['primaryContents']['sectionListRenderer']  
        results = results['contents'][0]
        results = results['itemSectionRenderer']['contents']
        return results
    
    @staticmethod
    def __get_initial_data(content: str) -> dict:
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
    async def fetch_from_search(self, query: str) -> Video:
        urlsafe_quote = urllib.parse.quote(query)
        url = 'https://www.youtube.com/results?search_query=' + urlsafe_quote
        resp = await self.client.get(url)
        resp.raise_for_status()
        content = resp.content.decode()
        try:    
            ytInitialData = self.__get_initial_data(content)
            results = self.__get_results(ytInitialData) # the videos
            for result in results:
                if 'videoRenderer' in result:
                    videoId = result['videoRenderer']['videoId']
                    result = await self.fetch_from_video(videoId)
                    return result
            raise VideoSearchNotFound(query)
        except VideoSearchNotFound:
            raise VideoSearchNotFound(query)


    async def fetch_from_video(self, videoId: str) -> list[Video]:
        request = self.youtube.videos().list(
            part='snippet',
            id=videoId
        )
        with concurrent.futures.ThreadPoolExecutor() as pool:
            r = await self.loop.run_in_executor(
                pool, request.execute
            )
        if r['items'] != []:
            result = _parse_data(
                data=r['items'][0],
                videoId=videoId,
                from_playlist=False
            )
            return result
        else:
            raise VideoUnavailable()


    async def fetch_from_playlist(self, playlistId: str) -> list[Video]:
        request = self.youtube.playlistItems().list(
            part='snippet',
            playlistId=playlistId,
            maxResults=1000
        )
        items = []
        with concurrent.futures.ThreadPoolExecutor() as pool:
            while request != None:
                r = await self.loop.run_in_executor(
                    pool, request.execute
                )
                items += r['items']
                request = self.youtube.playlistItems().list_next(request, r)
        songs = [
            _parse_data(
                data=song,
                videoId=song['snippet']['resourceId']['videoId'],
                from_playlist=True
            ) for song in items
        ]
        return songs


    async def fetch_channel_icon(self, channelId) -> str:
        request = self.youtube.channels().list(
            part='snippet',
            id=channelId
        )
        with concurrent.futures.ThreadPoolExecutor() as pool:
            r = await self.loop.run_in_executor(
                pool, request.execute
            )
        icon = r['items'][0]['snippet']['thumbnails']['default']['url']
        return icon

async def get_raw_url(url): # scraping instead of using yt_dlp for async
    query = parse_qs(urlparse(url).query, keep_blank_values=True)
    url = urllib.parse.quote('https://www.youtube.com/watch?v=' + query['v'][0])
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'https://loader.to/ajax/download.php?format=1080&url={url}')
        resp.raise_for_status()
        resp_json = resp.json()
        ID = resp_json['id']
        condition = True
        while condition:
            await asyncio.sleep(1)
            resp = await client.get(f'https://loader.to/ajax/progress.php?id={ID}')
            resp.raise_for_status()
            resp_json = resp.json()
            condition = resp_json['success'] == 0
    return resp_json['download_url']