import urllib.parse
import httpx
from utility.common.errors import VideoUnavailable

client = httpx.AsyncClient()
get_url = 'https://line.1010diy.com/web/free-mp3-finder/detail?url=%s&phonydata=false'

async def get_raw_url(url):
    url = urllib.parse.quote(url)
    resp = await client.get(get_url % url)
    resp.raise_for_status()
    data = resp.json()
    data = data['data']
    for video in data['videos']:
        return video['url']
    raise VideoUnavailable()