from utility.scraping import YouTube, Reddit, TikTok, Spotify
from utility.common.errors import UnsupportedUrl, DownloadFailure
from utility.common.requests import get_redirect_url
from urllib.parse import urlparse
import urllib.request
import os


supported_sites = {
    'www.youtube.com': (YouTube.get_raw_url, lambda _: 'mp4'),
    'www.reddit.com': (Reddit.get_raw_url, lambda url: os.path.splitext(urlparse(url).path)[1] if '?' not in url else 'mp4'),
    'www.tiktok.com': (TikTok.get_raw_url, lambda _: 'mp4'),
    'open.spotify.com': (Spotify.get_raw_url, lambda _: 'mp3')
}


async def fetch_url(url: str, host: str):
    get_raw_url, ext = supported_sites[host]
    try:
        raw_url = await get_raw_url(url)
        return raw_url, ext(raw_url)
    except DownloadFailure:
        raise DownloadFailure()


async def from_url(url):
    url = await get_redirect_url(url)
    parsed = urlparse(url)
    host = parsed.hostname
    if host in supported_sites.keys():
        return await fetch_url(url, host)
    raise UnsupportedUrl()
