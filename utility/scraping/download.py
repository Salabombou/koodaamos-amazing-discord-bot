from utility.scraping import YouTube, Reddit, TikTok, Spotify
from utility.common.errors import UnsupportedUrl
import urllib.parse
import urllib.request
import os

supported_sites = ['www.youtube.com', 'www.reddit.com', 'www.tiktok.com', 'open.spotify.com']

async def fetch_url(url, host):
    if host == 'www.youtube.com':
        return YouTube.get_raw_url(url, video=True, max_duration=300), 'mp4'
    if host == 'www.reddit.com':
        url = await Reddit.get_raw_url(url)
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        return url, ext
    if host == 'www.tiktok.com':
        url = await TikTok.get_raw_url(url)
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        return url, ext
    if host == 'open.spotify.com':
        url = await Spotify.get_raw_url(url)
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        return url, 'mp3'
     
async def from_url(url):
    resp = urllib.request.urlopen(url)
    parsed = urllib.parse.urlparse(resp.url)
    host = parsed.hostname
    if host in supported_sites:
        return await fetch_url(url, host)
    raise UnsupportedUrl()