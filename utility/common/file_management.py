import validators
import httpx
import io
import discord
from utility.scraping import pomf
from utility.ffmpeg import compress
from discord.ext import bridge
from utility.common import decorators

client = httpx.AsyncClient()

#@decorators.Async.logging.log
async def get_bytes(file) -> bytes:  # returns the bytes of the file to be converted
    """
        Gets the bytes from a file or a url
    """
    if not isinstance(file, bytes):  # if it is not already bytes
        if validators.url(file):  # if its from the web
            resp = await client.get(file)
            resp.raise_for_status()
            file = resp.content
        else:  # if its stored in a directory somewhere locally
            with open(file, 'rb') as f:
                file = f.read()
    return file


async def prepare_file(ctx: bridge.BridgeExtContext | bridge.BridgeApplicationContext, file: bytes | str, ext, _compressed: bool = False) -> str | discord.File:
    """
        Prepares the to be sended file
    """
    file = await get_bytes(file)
    filesize = len(file)
    filesize_limit = ctx.guild.filesize_limit
    if filesize < 75 * 1000 * 1000 and not filesize < filesize_limit:
        pomf_url = await pomf.upload(file, ext)
        return pomf_url, None
    elif not filesize < filesize_limit and not _compressed:
        file = await compress.video(file)
        return await prepare_file(ctx, file, ext, True)
    file = io.BytesIO(file)
    file = discord.File(fp=file, filename='unknown.' + ext)
    return '', file
