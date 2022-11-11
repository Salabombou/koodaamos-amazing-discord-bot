from urllib.parse import quote
import httpx
import json
import asyncio
import bs4
from utility.common.errors import GeniusSongsNotFound

class GeniusSearchResults:
    def __init__(self, results: dict) -> None:
        self.json = results
        self.song_results = [self.SongResult(**result['result']) for result in results['hits'] if result['type'] == 'song']
        self.best_song_result = self.song_results[0]

    class SongResult:
        def __init__(
            self, *,
            api_path: str,
            artist_names: str,
            full_title: str,
            id: int,
            language: str,
            lyrics_owner_id: int,
            lyrics_state: str,
            path: str,
            release_date_components: dict,
            title: str,
            url: str,
            **kwargs
        ) -> None:
            self.api_path = api_path
            self.artist_names = artist_names
            self.title = title
            self.full_title = full_title
            self.id = id
            self.language = language
            self.lyrics_owner_id = lyrics_owner_id
            self.lyrics_state = lyrics_state
            self.path = path
            self.release_date = release_date_components
            self.url = url
            self.lyrics = None

        async def GetLyrics(self) -> str:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.url)
                resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features='lxml')
            divs = soup.select('div[data-lyrics-container="true"]')
            lyrics = ''
            for div in divs:
                lyrics += '\n\n'.join([content for content in div.contents if isinstance(content, str)]) + '\n\n'
            self.lyrics = lyrics
            return lyrics


class Genius:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.search_url = f'https://api.genius.com/search?access_token={access_token}&q='
    
    async def Search(self, query: str) -> GeniusSearchResults:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.search_url + quote(query))
            resp.raise_for_status()
        response = resp.json()['response']

        if response['hits'] == []:
            raise GeniusSongsNotFound(query)

        results = GeniusSearchResults(resp.json()['response'])
        return results