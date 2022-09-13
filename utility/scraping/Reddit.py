import httpx
import bs4
import urllib.parse

client = httpx.AsyncClient(timeout=10)

async def get_raw_url(url):
    url = urllib.parse.quote(url)
    redditsave_url = 'https://redditsave.com/info?url=' + url
    resp = await client.get(redditsave_url)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features='lxml')
    soup = soup.find_all('a', class_='downloadbutton')[0]
    return soup['href']