from asyncio import AbstractEventLoop
import functools
import googleapiclient.discovery
import json
import yt_dlp
import urllib
import urllib.parse
import urllib.request
import validators
from utility.common.errors import UrlInvalid, VideoTooLong, VideoSearchNotFound, VideoUnavailable
import httpx
import re
import concurrent.futures
from utility.common.string import zero_width_space as zws

class Video:  # for the video info
    def __init__(self, data=None):
        if data is None:
            data = {
                'title': zws,
                'description': zws,
                'resourceId': {'videoId': zws},
                'channelId': zws,
                'videoOwnerChannelId': zws,
                'videoOwnerChannelTitle': zws
            }
        self.title = data['title'][0:256]  # just incase
        self.description = data['description'][0:4096]  # just incase
        self.channel = '???'
        self.id = data['resourceId']['videoId']
        self.thumbnail = f'https://i.ytimg.com/vi/{self.id}/mqdefault.jpg'
        self.channelId = data['channelId']
        # if i can retrieve these stuff
        if data['title'] != 'Private video' and data['title'] != 'Deleted video':
            self.channel = data['videoOwnerChannelTitle']
            self.channelId = data['videoOwnerChannelId']

class YT_Extractor:
    def __init__(self, loop: AbstractEventLoop, yt_api_key: str=None) -> None:
        self.loop = loop
        self.youtube = None
        if not yt_api_key is None:
            self.youtube = googleapiclient.discovery.build(
                'youtube', 'v3', developerKey=yt_api_key
            )
        self.client = httpx.AsyncClient()

    async def get_raw_url(self, url, video=False, max_duration=None):
        info = await self.get_info(url=url, video=video, max_duration=max_duration)
        return info['url']

    async def get_info(self, url, video=False, max_duration=None):
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
            info['url'] = urllib.request.urlopen(info['url']).url
            if max_duration != None:
                if info['duration'] < max_duration:
                    return info
            else:
                return info
            raise VideoTooLong(max_duration)


    # youtube api searches are expensive so webscraping it is
    async def fetch_from_search(self, query) -> Video:
        urlsafe_quote = urllib.parse.quote(query)
        url = 'https://www.youtube.com/results?search_query=' + urlsafe_quote
        resp = await self.client.get(url)
        resp.raise_for_status()
        content = resp.content.decode('utf-8')
        try:    
            # gets the variable that contains the search results
            ytInitialData = re.findall('var ytInitialData = .*};', content)
            # removes the variable declaration itself
            ytInitialData: str = ytInitialData[0][20:]
            # trims the end of any gunk that would otherwise run the conversion
            ytInitialData = ytInitialData.split('};')[0] + '}'
            ytInitialData = json.loads(ytInitialData)  # str => dict
            results = ytInitialData['contents']['twoColumnSearchResultsRenderer']['primaryContents'][
                'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']  # the videos
            for result in results:
                if 'videoRenderer' in result:
                    videoId = result['videoRenderer']['videoId']
                    return await self.fetch_from_video(videoId)[0]
            raise VideoSearchNotFound(query)
        except VideoSearchNotFound:
            raise VideoSearchNotFound(query)


    async def fetch_from_video(self, videoId) -> list[Video]:
        request = self.youtube.videos().list(
            part='snippet',
            id=videoId
        )
        with concurrent.futures.ThreadPoolExecutor() as pool:
            r = await self.loop.run_in_executor(
                pool, request.execute
            )
        if r['items'] != []:
            r['items'][0]['snippet']['resourceId'] = {'videoId': videoId}
            song = r['items'][0]['snippet']
            song['videoOwnerChannelTitle'] = song['channelTitle']
            song['videoOwnerChannelId'] = song['channelId']
            return [Video(data=song)]
        else:
            raise VideoUnavailable()


    async def fetch_from_playlist(self, playlistId) -> list[Video]:
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
        songs = []
        for song in items:
            song = song['snippet']
            songs.append(Video(data=song))
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