import asyncio
import urllib.request
import concurrent.futures
from utility.common.errors import UrlRedirectError
from utility.common import decorators
loop = asyncio.get_event_loop()

@decorators.Async.logging.log
async def get_redirect_url(url: str):
    """
        Gets the redirect url from url
    """
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for _ in range(10):
            resp = await loop.run_in_executor(
                pool,
                urllib.request.urlopen, url
            )
            redirected = url != resp.url
            url = resp.url
            if not redirected:
                return url
    raise UrlRedirectError('Url redirected too many times')
