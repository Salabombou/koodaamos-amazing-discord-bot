import yt_dlp
import urllib
import validators

class Video: # for the video info
    def __init__(self, data={
        'title': '​',
        'description': '​',
        'resourceId': {'videoId': '​'},
        'channelId': '​',
        'videoOwnerChannelId': '​',
        'videoOwnerChannelTitle': '​'
        }):
        self.title = data['title'][0:256] # just incase
        self.description = data['description'][0:4096] # just incase
        self.channel = '???'
        self.id = data['resourceId']['videoId']
        self.thumbnail = f'https://i.ytimg.com/vi/{self.id}/mqdefault.jpg'
        self.channelId = data['channelId']
        if data['title'] != 'Private video' and data['title'] != 'Deleted video': # if i can retrieve these stuff
            self.channel = data['videoOwnerChannelTitle']
            self.channelId = data['videoOwnerChannelId']

def get_raw_url(url, video=False, max_duration=None):
    info = get_info(url=url, video=video, max_duration=max_duration)
    return info['url']

def get_info(url, video=False, max_duration=None):
    if not validators.url(url): raise Exception('Invalid url.')
    ydl_opts = {
        'format': 'bestaudio/best',
        'throttled-rate': '180K',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
    }
    if video: ydl_opts['format'] = 'mp4'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        info['url'] = urllib.request.urlopen(info['url']).url
        if max_duration != None:
            if info['duration'] < max_duration:
                return info
        else: return info
        raise Exception('Video is too long to be downloaded.')

def fetch_from_search(youtube, query):
    request = youtube.search().list(
        part='snippet',
        maxResults=1,
        type='video', # only videos
        safeSearch='none',
        q=query
    )
    r = request.execute()
    if len(r['items']) > 0:
        videoId = r['items'][0]['id']['videoId']
        return fetch_from_video(youtube, videoId=videoId)
    raise Exception(f"No videos were found with the query '{query}'")
    

def fetch_from_video(youtube, videoId):
    request = youtube.videos().list(
        part='snippet',
        id=videoId
    )
    r = request.execute()
    r['items'][0]['snippet']['resourceId'] = {'videoId': videoId}
    song = r['items'][0]['snippet']
    song['videoOwnerChannelTitle'] = song['channelTitle']
    song['videoOwnerChannelId'] = song['channelId']
    return [Video(data=song)]

async def fetch_from_playlist(ctx, youtube, playlistId):
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlistId,
        maxResults=1000
    )
    items = []
    while request != None:
        r = await ctx.bot.loop.run_in_executor(None, request.execute)
        items += r['items']
        request = youtube.playlistItems().list_next(request, r)
    songs = []
    for song in items:
        song = song['snippet']
        songs.append(Video(data=song))
    return songs

def fetch_channel_icon(youtube, channelId):
    request = youtube.channels().list(
        part='snippet',
        id=channelId
    )
    r = request.execute()
    icon = r['items'][0]['snippet']['thumbnails']['default']['url']
    return icon