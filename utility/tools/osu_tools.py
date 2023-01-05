import httpx
from requests_toolbelt import MultipartEncoder
import urllib.parse
import websocket

client = httpx.AsyncClient()

fields = {
    'username': '',
    'replayFile': ['replay.osr', None, 'application/octet-stream'],
    'resolution': '1280x720',
    'globalVolume': '100',
    'musicVolume': '100',
    'hitsoundVolume': '100',
    'useSkinHitsounds': 'false',
    'playNightcoreSamples': 'true',
    'showHitErrorMeter': 'true',
    'showScore': 'true',
    'showHPBar': 'true',
    'showComboCounter': 'true',
    'showPPCounter': 'false',
    'showKeyOverlay': 'true',
    'showScoreboard': 'false',
    'showAvatarsOnScoreboard': 'false',
    'showBorders': 'false',
    'showMods': 'true',
    'showResultScreen': 'true',
    'showHitCounter': 'true',
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
    'showDanserLogo': 'true',
    'skip': 'true',
    'cursorRipples': 'false',
    'sliderSnakingIn': 'true',
    'sliderSnakingOut': 'true',
    'cursorSize': '1',
    'cursorTrail': 'true',
    'showUnstableRate': 'true',
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
    'verificationKey': 'devmode_success'
}

async def get_replay(replay: bytes, username: str):
    fields['username'] = username
    fields['replayFile'][1] = replay
    data = MultipartEncoder(fields=fields)

    ws = await client.get('wss://ordr-ws.issou.best/')
    pass

