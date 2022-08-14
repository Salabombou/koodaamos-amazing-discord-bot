import httpx
import asyncio
from requests_toolbelt import MultipartEncoder
import validators

async def get_bytes(file):
    if validators.url(file):
        r = await httpx.AsyncClient().get(file)
        r.raise_for_status()
        file = r.content
    elif not isinstance(file, bytes):
        with open(file, 'rb') as f:
            file = f.read()
            f.close()
    return file

async def get_token():
    r = await httpx.AsyncClient().post(url='https://transcode-f36588.8mb.video', headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data='preflight=true')
    r.raise_for_status()
    token = r.json()['token']
    return token

async def wait_for_completion(token):
    condition = True
    while condition: # do while in python :PogU:
        await asyncio.sleep(1)
        r = await httpx.AsyncClient().get(f'https://transcode-d0ad0a.8mb.video/check-progress?token={token}')
        r.raise_for_status()
        condition = r.json()['status'] != 'Done'
    return

async def video(file : bytes | str) -> bytes: # compressing using the 8mb.video website
    file = await get_bytes(file)
    token = await get_token()
    fields = {
        'hq': 'true',
        'size': '8',
        'token': token,
        'submit': 'true',
        'fileToUpload': ('video.mp4', file, 'video/mp4') # filename, file in bytes, filetype
    }
    data = MultipartEncoder(fields=fields)
    async with httpx.AsyncClient() as requests:        
        r = await requests.post(url='https://transcode-d0ad0a.8mb.video', headers={'Content-Type': data.content_type}, data=data.to_string()) # initialize the compression
        r.raise_for_status()
        await wait_for_completion(token) # waits for the compressed video to be ready
        r = await requests.get(f'https://transcode-d0ad0a.8mb.video/8mb.video-{token}.mp4') # downloads the compressed video
        r.raise_for_status()
    return r.content # returns the compressed video as bytes