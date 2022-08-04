import yt_dlp

class Video: # for the video info
    def __init__(self, data={
        'title': '​',
        'description': '​',
        'resourceId': {'videoId': '​'},
        'channelId': '​',
        'videoOwnerChannelTitle': '​',
        'thumbnails': {'high': {'url': '​'}}
    }):
        self.title = data['title'][0:256] # just incase
        self.description = data['description'][0:4096] # just incase
        self.channel = '???'
        self.thumbnail = None
        self.id = data['resourceId']['videoId']
        self.channelId = data['channelId']
        if data['title'] != 'Private video' and data['title'] != 'Deleted video': # if i can retrieve these stuff
            self.channel = data['videoOwnerChannelTitle']
            self.thumbnail = data['thumbnails']['high']['url']
        #self.duration = '​'

ydl_opts = {
    'format': 'bestaudio/best',
    'sponsorblock-remove': 'all',
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
async def ExtractInfo(url, audio=False):
    ydl_opts['format'] = 'mp4'
    if audio:
        ydl_opts['format'] = '140'
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
            info = ydl.extract_info(url, download=False)
            url = info['url']
            return url
        except:
            return ydl.extract_info('https://www.youtube.com/watch?v=J3lXjYWPoys', download=False)['url']

def fetch_from_search(youtube, query):
    request = youtube.search().list(
        part='snippet',
        maxResults=3,
        safeSearch='none',
        q=query
    )
    r = request.execute()
    if len(r['items']) > 0:
        videoId = r['items'][0]['id']['videoId']
        return fetch_from_video(youtube, videoId=videoId)
    raise Exception(f"No videos were found with the following query: '{query}'")

def fetch_from_video(youtube, videoId):
    request = youtube.videos().list(
        part='snippet',
        id=videoId
    )
    r = request.execute()
    r['items'][0]['snippet']['resourceId'] = {'videoId': videoId}
    song = r['items'][0]['snippet']
    song['videoOwnerChannelTitle'] = song['channelTitle']
    return [Video(data=song)]

async def fetch_from_playlist(youtube, playlistId):
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlistId,
        maxResults=1
    )
    r = request.execute()
    song = r['items'][0]['snippet']
    return Video(data=song)

def fetch_channel_icon(youtube, channelId):
    request = youtube.channels().list(
        part='snippet',
        id=channelId
    )
    r = request.execute()
    return r['items'][0]['snippet']['thumbnails']['default']['url']