import yt_dlp

ydl_opts = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
async def ExtractInfo(url, audio=False):
    ydl_opts['format'] = 'mp4'
    if audio:
        ydl_opts['format'] = 'bestaudio/best'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        try:
            duration = info['duration']
        except:
            raise Exception("Invalid url")
        if duration > 180:
            raise Exception("Video is too long. Maximum video length is 3 minutes")
        else:
            return info

def get_raw_audio_url(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)['url']
        except:
            return ydl.extract_info('https://www.youtube.com/watch?v=J3lXjYWPoys', download=False)['url']