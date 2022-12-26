import httpx
import asyncio
from requests_toolbelt import MultipartEncoder
import re
import json
from utility.common import file_management, decorators

client = httpx.AsyncClient(timeout=10)


async def get_host():
    """
        Gets the best server that is online to be used to compress the video
    """
    website = await client.get('https://8mb.video/')
    webpage_source = website.content.decode('utf-8')
    hosts_online: str = re.findall('var hosts_online = .*"];', webpage_source)[0]
    hosts_online = hosts_online.replace('var hosts_online = ', '')[:-1]
    hosts_online = json.loads(hosts_online)
    host = 'https://' + hosts_online[0]
    return host


async def get_token(host):
    """
        Creates the compression instance at the server and returns the token of the said instance
    """
    resp = await client.post(url=host, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data='preflight=true')
    resp.raise_for_status()
    token = resp.json()['token']
    return token


async def wait_for_completion(host, token):
    """
        Waits for the compression to be finished
    """
    condition = True
    while condition:  # do while in python :PogU:
        await asyncio.sleep(1)
        resp = await client.get(host + f'/check-progress?token={token}')
        resp.raise_for_status()
        condition = resp.json()['status'] != 'Done'
    return

upload_limit_levels = ['8', '8', '50', '100']

#@decorators.Async.logging.log
async def video(file: bytes | str, server_level, ext) -> bytes | str:
    """
        Compressing videos using the 8mb.video website so the video can be sent to discord channel
    """
    file = await file_management.get_bytes(file)
    size = upload_limit_levels[server_level]
    host = await get_host()
    token = await get_token(host)
    fields = {
        'hq': 'true',
        'size': size,
        'token': token,
        'submit': 'true',
        # filename, file in bytes, filetype
        'fileToUpload': (f'file.{ext}', file, 'application/octet-stream')
    }
    data = MultipartEncoder(fields=fields)
    # sends the video to be compressed to the server and begins the compression
    resp = await httpx.AsyncClient(timeout=300).post(url=host, headers={'Content-Type': data.content_type}, data=data.to_string(), timeout=60)
    resp.raise_for_status()

    # waits for the compressed video to be ready
    await wait_for_completion(host, token)
    # downloads the compressed video
    resp = await client.get(host + f'/8mb.video-{token}.mp4')
    resp.raise_for_status()

    return resp.content  # returns the compressed video as bytes
