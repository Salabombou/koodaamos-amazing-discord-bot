import httpx
import asyncio
from requests_toolbelt import MultipartEncoder
import validators
import re
import ast

async def get_host():
    website = await httpx.AsyncClient().get('https://8mb.video/')
    hosts_online = re.findall('var hosts_online = .*"];', str(website.content))[0].replace('var hosts_online = ', '')[:-1]
    hosts_online = ast.literal_eval(hosts_online)
    host = hosts_online[0]
    return 'https://' + host

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

async def get_token(host):
    r = await httpx.AsyncClient().post(url=host, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data='preflight=true')
    r.raise_for_status()
    token = r.json()['token']
    return token

async def wait_for_completion(host, token):
    condition = True
    while condition: # do while in python :PogU:
        await asyncio.sleep(1)
        r = await httpx.AsyncClient().get(host + f'/check-progress?token={token}')
        r.raise_for_status()
        condition = r.json()['status'] != 'Done'
    return

async def video(file : bytes | str) -> bytes: # compressing using the 8mb.video website
    host = await get_host()
    file = await get_bytes(file)
    token = await get_token(host)
    fields = {
        'hq': 'true',
        'size': '8',
        'token': token,
        'submit': 'true',
        'fileToUpload': ('video.mp4', file, 'video/mp4') # filename, file in bytes, filetype
    }
    data = MultipartEncoder(fields=fields)
    async with httpx.AsyncClient() as requests:        
        r = await requests.post(url=host, headers={'Content-Type': data.content_type}, data=data.to_string()) # initialize the compression
        r.raise_for_status()
        await wait_for_completion(host, token) # waits for the compressed video to be ready
        r = await requests.get(host + f'/8mb.video-{token}.mp4') # downloads the compressed video
        r.raise_for_status()
    return r.content # returns the compressed video as bytes