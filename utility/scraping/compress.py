import httpx
import asyncio
from requests_toolbelt import MultipartEncoder
import validators
import re
import ast

client = httpx.AsyncClient(timeout=10)

async def get_host(): # gets the best server that is online to be used to compress the video
    website = await client.get('https://8mb.video/')
    webpage_source = website.content.decode('utf-8')
    hosts_online = re.findall('var hosts_online = .*"];', webpage_source)[0].replace('var hosts_online = ', '')[:-1]
    hosts_online = ast.literal_eval(hosts_online)
    host = 'https://' + hosts_online[0]
    return host

async def get_bytes(file): # returns the bytes of the file to be converted
    if not isinstance(file, bytes): # if it is not already bytes
        if validators.url(file): # if its from the web
            resp = await client.get(file)
            resp.raise_for_status()
            file = resp.content
        else: # if its stored in a directory somewhere locally
            with open(file, 'rb') as f:
                file = f.read()
                f.close()
    return file

async def get_token(host): # creates the compression instance at the server and returns the token of the said instance
    resp = await client.post(url=host, headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}, data='preflight=true')
    resp.raise_for_status()
    token = resp.json()['token']
    return token

async def wait_for_completion(host, token): # waits for the compression to be finished
    condition = True
    while condition: # do while in python :PogU:
        await asyncio.sleep(1)
        resp = await client.get(host + f'/check-progress?token={token}')
        resp.raise_for_status()
        condition = resp.json()['status'] != 'Done'
    return

upload_limit_levels = ['8', '8', '50', '100']

async def video(file : bytes | str, ctx) -> bytes: # compressing videos using the 8mb.video website so the video can be sent to discord channel
    file = await get_bytes(file)
    filesize_limit = ctx.guild.filesize_limit
    filesize = len(file)
    if filesize < filesize_limit:
        return file # no need to compress
    server_level = ctx.guild.premium_tier
    size = upload_limit_levels[server_level]
    host = await get_host()
    token = await get_token(host)
    fields = {
        'hq': 'true',
        'size': size,
        'token': token,
        'submit': 'true',
        'fileToUpload': ('video.mp4', file, 'video/mp4') # filename, file in bytes, filetype
    }
    data = MultipartEncoder(fields=fields)
    resp = await httpx.AsyncClient(timeout=300).post(url=host, headers={'Content-Type': data.content_type}, data=data.to_string(), timeout=60) # sends the video to be compressed to the server and begins the compression
    resp.raise_for_status()

    await wait_for_completion(host, token) # waits for the compressed video to be ready
    resp = await client.get(host + f'/8mb.video-{token}.mp4') # downloads the compressed video
    resp.raise_for_status()
    
    return resp.content # returns the compressed video as bytes