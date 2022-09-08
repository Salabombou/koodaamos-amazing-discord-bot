import asyncio
import httpx
import random
import os

client = httpx.AsyncClient()
proxies = []

def get_url(): # https://www.webshare.io/
    file = open(os.getcwd() + "/files/tokens", "r")
    return file.read().split("\n")[4]

async def update_proxies():
    global proxies
    url = get_url()
    while True:
        resp = await client.get(url)
        resp.raise_for_status()
        proxies = resp.content.decode('utf-8').split('\r\n')
        await asyncio.sleep(300)
asyncio.ensure_future(update_proxies())

async def get_proxy():
    rand = random.randint(0, len(proxies) - 1)
    proxy = proxies[rand].split(':')
    return {'https://': f'http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}'} # username:password@ip:port



