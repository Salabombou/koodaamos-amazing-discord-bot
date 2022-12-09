import httpx
import bs4
import urllib.parse
from utility.common import decorators
from utility.common import config

client = httpx.AsyncClient(timeout=10)

@decorators.Async.logging.log
async def get_raw_url(url: str) -> str:
    """
        Gets the raw url of the file from Reddit
    """
    url = urllib.parse.quote(url)
    redditsave_url = 'https://redditsave.com/info?url=' + url
    resp = await client.get(redditsave_url)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)
    soup = soup.find_all('a', class_='downloadbutton')[0]
    return soup['href']
