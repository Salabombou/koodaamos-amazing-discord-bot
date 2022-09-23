import asyncio
import os
import validators
import httpx
import io
import discord
from utility.scraping import compress, pomf
import time
import threading

client = httpx.AsyncClient()

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

async def delete_temps(*args):
    await asyncio.sleep(10)
    for temp in args:
        try:
            os.remove(temp)
        except: print('Failed to delete file ' + temp)

async def prepare_file(ctx, file: bytes | str, ext) -> str | discord.File:
    file = await get_bytes(file)
    filesize = len(file)
    filesize_limit = ctx.guild.filesize_limit
    server_level = ctx.guild.premium_tier
    if filesize < 75 * 1000 * 1000 and not filesize < filesize_limit:
        pomf_url = await pomf.upload(file)
        return pomf_url, None
    elif not filesize < filesize_limit:
        file = await compress.video(file, server_level)
    file = io.BytesIO(file)
    file = discord.File(fp=file, filename='unknown.' + ext)
    return '', file

class TempRemover:
    def __init__(self) -> None:
        self.deleter = threading.Thread(target=self.delete_temps)
    def delete_temps(self):
        while True:
            current_time = time.time()
            for root, dirs, files in os.walk('./files', topdown=False):
                for file in files:
                    ext = os.path.splitext(file)[1][1:]
                    if ext == 'temp':
                        t_stamp = int(file.split('_')[1][:-5])
                        if current_time - t_stamp > 300:
                            os.remove(f'{root}/{file}')
            time.sleep(10)
    
    def start(self):
        self.deleter.start()
