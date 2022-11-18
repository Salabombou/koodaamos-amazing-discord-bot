from urllib.parse import quote
import httpx
import numpy as np
import bs4
from utility.common.errors import GeniusSongsNotFound

class GeniusSearchResults:
    """
        A class object for genius search results
    """
    def __init__(self, results: dict) -> None:
        self.json = results
        self.song_results = [self.SongResult(**result['result']) for result in results['hits'] if result['type'] == 'song']
        self.best_song_result = self.song_results[0]

    class SongResult:
        """
            A class object for invidual songs from the results
        """
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
            header_image_thumbnail_url: str = '',
            primary_artist: dict[str],
            **other
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
            self.thumbnail = header_image_thumbnail_url
            self.artist_icon = primary_artist['image_url']
            self.other = other
            self.lyrics = None
        
        def __parse_results(self, contents: bs4.element.Tag) -> list[str]:
            results = []
            for content in contents:
                if isinstance(content, str):
                    results.append(content)
                
                if not isinstance(content, bs4.element.Tag):
                    continue

                if content.string != None:
                    results.append(content.text)
                else:
                    results += self.__parse_results(content.contents)
                    
            return results

        async def GetLyrics(self) -> str:
            """
                Gets the lyrics from the song
            """
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.url)
                resp.raise_for_status()
            soup = bs4.BeautifulSoup(resp.content, features='lxml')
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
    
    async def Search(self, query: str) -> GeniusSearchResults:
        """
            Searches for lyrics from genius api
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.search_url + quote(query))
            resp.raise_for_status()
        response = resp.json()['response']

        if response['hits'] == []:
            raise GeniusSongsNotFound(query)

        results = GeniusSearchResults(resp.json()['response'])
        return results