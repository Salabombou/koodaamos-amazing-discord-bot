import asyncio
import os
import validators
import httpx

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