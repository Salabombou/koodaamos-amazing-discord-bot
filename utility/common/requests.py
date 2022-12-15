from utility.common import decorators
import httpx

@decorators.Async.logging.log
async def get_redirect_url(url: str) -> str:
    """
        Gets the redirect url from url
    """
    async with httpx.AsyncClient(follow_redirects=True, max_redirects=10) as client:
        resp = await client.head(url)
        resp.raise_for_status()
    redirect_url = str(resp.url)
    return redirect_url
