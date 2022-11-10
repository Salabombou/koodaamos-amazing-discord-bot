from utility.scraping import YouTube, Reddit, TikTok, Spotify
from utility.common.errors import UnsupportedUrl, DownloadFailure
from utility.common.requests import get_redirect_url
import urllib.parse
import urllib.request
import os

supported_sites = [
    'www.youtube.com',
    'www.reddit.com',
    'www.tiktok.com',
    'open.spotify.com'
]



def get_extension(url: str):
    path = urllib.parse.urlparse(url.split('?')[1]).path[1:]
    ext = os.path.splitext(path)[1][1:]
    ext = ext if ext != '' else 'mp4'
    return ext

async def fetch_url(url: str, host: str):
    try:
        match host:
            case 'www.youtube.com':
                return await YouTube.get_raw_url(url), 'mp4'
            case 'www.tiktok.com':
                return await TikTok.get_raw_url(url), 'mp4'
            case 'open.spotify.com':
                return await Spotify.get_raw_url(url), 'mp3'
            case 'www.reddit.com':
                url = await Reddit.get_raw_url(url)
                return url, get_extension(url)
        raise DownloadFailure()
    except DownloadFailure:
        raise DownloadFailure()


async def from_url(url):
    url = await get_redirect_url(url)
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if host in supported_sites:
        return await fetch_url(url, host)
    raise UnsupportedUrl()
