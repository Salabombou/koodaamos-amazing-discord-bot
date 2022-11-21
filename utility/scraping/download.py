import os
from urllib.parse import urlparse

from utility.common import decorators
from utility.common.errors import DownloadFailure, UnsupportedUrl
from utility.common.requests import get_redirect_url
from utility.scraping import Reddit, Spotify, TikTok, YouTube

supported_sites = { # sites supported by the downloader
    'www.youtube.com': (YouTube.get_raw_url, lambda _: 'mp4'),
    'www.reddit.com': (Reddit.get_raw_url, lambda url: os.path.splitext(urlparse(url).path)[1] if '?' not in url else 'mp4'),
    'www.tiktok.com': (TikTok.get_raw_url, lambda _: 'mp4'),
    'open.spotify.com': (Spotify.get_raw_url, lambda _: 'mp3')
}


async def __fetch_url(url: str, get_raw_url, ext):
    """
        Fetches the raw url and the file extension from the url
    """
    try:
        raw_url = await get_raw_url(url)
        return raw_url, ext(raw_url)
    except DownloadFailure:
        raise DownloadFailure()

@decorators.Async.logging.log
async def from_url(url):
    """
        Gets the raw url to the file to be downloaded
    """
    url = await get_redirect_url(url)
    parsed = urlparse(url)
    host = parsed.hostname
    if host in supported_sites.keys():
        return await __fetch_url(url, *supported_sites[host])
    raise UnsupportedUrl()
