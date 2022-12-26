from asyncio import AbstractEventLoop
import httpx
from utility.common import decorators

class Spotify_Extractor: # WIP
    def __init__(self, loop: AbstractEventLoop) -> None:
        self.loop = loop
#@decorators.Async.logging.log
async def get_raw_url(url):
    """
        Gets the raw url of the song from spotify
    """
    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.post(
            url='https://api.spotify-downloader.com/',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='link=' + url
        )
    resp.raise_for_status()
    data = resp.json()
    return data['audio']['url']
