import httpx
import asyncio
from requests_toolbelt import MultipartEncoder
from utility.common.errors import Osr2Mp4Error

default_fields = {
    'replayURL': '',
    'username': '',
    'resolution': '1280x720',
    'globalVolume': '100',
    'musicVolume': '50',
    'hitsoundVolume': '100',
    'useSkinHitsounds': 'false',
    'playNightcoreSamples': 'true',
    'showHitErrorMeter': 'true',
    'showScore': 'true',
    'showHPBar': 'true',
    'showComboCounter': 'true',
    'showPPCounter': 'true',
    'showKeyOverlay': 'true',
    'showScoreboard': 'true',
    'showAvatarsOnScoreboard': 'false',
    'showBorders': 'false',
    'showMods': 'false',
    'showResultScreen': 'true',
    'showHitCounter': 'false',
    'showAimErrorMeter': 'false',
    'customSkin': 'false',
    'skin': 'YUGEN',
    'useSkinCursor': 'true',
    'useSkinColors': 'false',
    'useBeatmapColors': 'true',
    'cursorScaleToCS': 'false',
    'cursorRainbow': 'false',
    'cursorTrailGlow': 'false',
    'drawFollowPoints': 'true',
    'scaleToTheBeat': 'false',
    'sliderMerge': 'false',
    'objectsRainbow': 'false',
    'objectsFlashToTheBeat': 'false',
    'useHitCircleColor': 'true',
    'seizureWarning': 'false',
    'loadStoryboard': 'true',
    'loadVideo': 'true',
    'introBGDim': '0',
    'inGameBGDim': '75',
    'breakBGDim': '30',
    'BGParallax': 'false',
    'showDanserLogo': 'false',
    'skip': 'true',
    'cursorRipples': 'false',
    'sliderSnakingIn': 'true',
    'sliderSnakingOut': 'true',
    'cursorSize': '1',
    'cursorTrail': 'true',
    'showUnstableRate': 'false',
    'drawComboNumbers': 'true',
    'addPitch': 'false',
    'noDelete': 'false',
    'turboMode': 'false',
    'aimErrorMeterXPos': '1222',
    'aimErrorMeterYPos': '586',
    'ppCounterXPos': '5',
    'ppCounterYPos': '150',
    'hitCounterXPos': '5',
    'hitCounterYPos': '195',
    #'verificationKey': 'devmode_success'
}

async def __wait_for_completion(ID: int):
    client = httpx.AsyncClient(timeout=10)
    url = 'https://apis.issou.best/ordr/renders?renderID=' + str(ID)
    
    render = {'progress': None}
    
    while render['progress'] != 'Done.':
        await asyncio.sleep(1)
        try:
            resp = await client.get(url)
        except httpx.ReadTimeout:
            continue
        resp.raise_for_status()
        
        render = resp.json()['renders'][0]
    
    return render['videoUrl']


async def get_replay(replay: str, username: str, no_hud=False):
    fields = default_fields.copy() # copy by value and not reference
    fields['username'] = username
    fields['replayURL'] = replay
    
    if no_hud:
        keys = ['showScore', 'showHPBar', 'showComboCounter', 'showPPCounter', 'showKeyOverlay', 'showScoreboard', 'showHitErrorMeter']
        for key in keys:
            fields[key] = str(False).lower() # false
    
    data = MultipartEncoder(fields=fields)
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url='https://apis.issou.best/ordr/renders',
            headers={'Content-Type': data.content_type},
            data=data.to_string()
        )
    resp_json = resp.json() if resp.status_code != 429 else {'errorCode': 429, 'message': resp.content.decode()}
    
    if resp_json['errorCode'] != 0:
        raise Osr2Mp4Error(resp_json['message'])
    
    resp.raise_for_status()
    
    video_url = await __wait_for_completion(ID=resp_json['renderID'])
    
    return video_url