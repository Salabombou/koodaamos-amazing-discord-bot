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

async def fetch_url(url, host):
    try:
        if host == 'www.youtube.com':
            return await YouTube.get_raw_url(url), 'mp4'
        elif host == 'www.tiktok.com':
            return await TikTok.get_raw_url(url), 'mp4'
        elif host == 'open.spotify.com':
            return await Spotify.get_raw_url(url), 'mp3'
        elif host == 'www.reddit.com':
            url: str = await Reddit.get_raw_url(url)
            path = urllib.parse.urlparse(url.split('?')[1]).path[1:]
            ext = os.path.splitext(path)[1][1:]
            ext = ext if ext != '' else 'mp4'
            return url, ext
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
