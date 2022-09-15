import asyncio
import os

async def delete_temps(*args):
    await asyncio.sleep(10)
    for temp in args:
        try:
            os.remove(temp)
        except: print('Failed to delete file ' + temp)