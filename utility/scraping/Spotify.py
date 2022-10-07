import httpx

client = httpx.AsyncClient(timeout=300)


async def get_raw_url(url):
    resp = await client.post(
        url='https://api.spotify-downloader.com/',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data='link=' + url
    )
    resp.raise_for_status()
    data = resp.json()
    return data['audio']['url']
