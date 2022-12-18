from utility.common import decorators
import httpx
from urllib.parse import unquote
@decorators.Async.logging.log
async def get_redirect_url(url: str) -> str:
    """
        Gets the redirect url from url
    """
    async with httpx.AsyncClient(follow_redirects=True, max_redirects=10) as client:
        resp = await client.head(url)
        resp.raise_for_status()
    redirect_url = str(resp.url)
    redirect_url = redirect_url if url not in unquote(redirect_url) else url
    return redirect_url
