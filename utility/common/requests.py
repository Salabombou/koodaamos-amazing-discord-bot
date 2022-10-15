import asyncio
import urllib.request
import concurrent.futures


loop = asyncio.get_event_loop()


async def get_redirect_url(url: str):
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while True:
            resp = await loop.run_in_executor(
                pool,
                urllib.request.urlopen, url
            )
            redirected = url != resp.url
            url = resp.url
            if not redirected:
                return url