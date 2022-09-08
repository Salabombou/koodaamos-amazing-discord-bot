import httpx
import bs4
import random

client = httpx.AsyncClient()

async def get_proxies():
    resp = await client.get('https://www.sslproxies.org/')
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features='lxml')
    proxies = soup.select('table.table.table-striped.table-bordered tbody tr')[:25]
    rand = random.randint(0, 24)
    proxy = proxies[rand]
    ip = proxy.contents[0].text
    port = proxy.contents[1].text
    return {'https://': f'http://{ip}:{port}'}



