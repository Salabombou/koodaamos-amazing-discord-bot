from urllib.parse import quote
import httpx
import numpy as np
import bs4
from utility.common.errors import GeniusSongsNotFound, GeniusApiError
from utility.common import decorators
from utility.common import config
from dataclasses import dataclass, field


class GeniusSearchResults:
    """
        A class object for genius search results
    """
    def __init__(self, results: dict) -> None:
        self.json = results
        self.song_results = [
            self.SongResult(
                **self.__parse_data(
                    result['result']
                )
            ) for result in results['hits'] if result['type'] == 'song'
        ]
        self.best_song_result = self.song_results[0] if self.song_results else None
    
    def __parse_data(self, data: dict):
        for key in list(data.keys()):
            if key not in self.SongResult().__dict__.keys():
                data.pop(key)
        data['primary_artist'] = data['primary_artist']['image_url']
        return data
    @dataclass(kw_only=True)
    class SongResult:
        """
            A class object for invidual songs from the results
        """
        api_path: str = field(repr=False, compare=False, default=None)
        artist_names: str = field(repr=True, compare=False, default=None)
        full_title: str = field(repr=False, compare=False, default=None)
        id: int = field(repr=False, compare=True, default=None)
        language: str = field(repr=False, compare=False, default=None)
        lyrics_owner_id: int = field(repr=False, compare=False, default=None)
        lyrics_state: str = field(repr=False, compare=False, default=None)
        release_date_components: dict = field(repr=False, compare=False, default=None)
        title: str = field(repr=True, compare=False, default=None)
        url: str = field(repr=False, compare=False, default=None)
        header_image_thumbnail_url: str = field(repr=False, compare=False, default=None)
        primary_artist: dict[str, str] = field(repr=False, compare=False, default=None)
        path: str = field(repr=False, compare=False, default=None)
        lyrics: str = field(repr=False, compare=False, default=None)
        
        def __parse_results(self, contents: bs4.element.Tag) -> list[str]:
            results = []
            for content in contents:
                if isinstance(content, str):
                    results.append(content)
                elif isinstance(content, bs4.element.Tag):
                    results += self.__parse_results(content.contents)
            return results
        
        #@decorators.Async.logging.log
        async def GetLyrics(self) -> str:
            """
                Gets the lyrics from the song
            """
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.url)
                resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)
            divs = soup.select('div[data-lyrics-container="true"]')
            
            contents = [self.__parse_results(div.contents) for div in divs]
            contents = list(np.hstack(contents))
            
            lyrics = ''
            lyrics += '\n\n'.join(contents) + '\n\n'
            self.lyrics = lyrics
            return lyrics


class Genius:
    """
        Used to get the lyrics from the genius website
    """
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.search_url = f'https://api.genius.com/search?access_token={access_token}&q='
    
    #@decorators.Async.logging.log
    async def Search(self, query: str) -> GeniusSearchResults:
        """
            Searches for lyrics from genius api
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.search_url + quote(query))
                resp.raise_for_status()
            response = resp.json()['response']
        except:
            raise GeniusApiError()
        if not response['hits']:
            raise GeniusSongsNotFound(query)
        results = GeniusSearchResults(resp.json()['response'])
        return results
