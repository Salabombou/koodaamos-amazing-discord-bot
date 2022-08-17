import httpx
import bs4
import urllib.parse

async def get_raw_url(url):
    url = urllib.parse.quote(url)
    redditsave_url = 'https://redditsave.com/info?url=' + url
    resp = await httpx.AsyncClient(timeout=10).get(redditsave_url)
    soup = bs4.BeautifulSoup(resp.content, features='lxml')
    soup = soup.find_all('a', class_='downloadbutton')[0]
    return soup['href']