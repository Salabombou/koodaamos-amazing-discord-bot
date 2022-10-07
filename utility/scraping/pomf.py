import httpx
from requests_toolbelt import MultipartEncoder
from utility.common.errors import PomfUploadFail

client = httpx.AsyncClient(timeout=300)


async def upload(file: bytes, ext: str) -> str:
    fields = {
        'files[]': (f'file.{ext}', file, 'application/octet-stream')
    }
    data = MultipartEncoder(fields=fields)
    resp = await client.post(url='https://pomf.cat/upload.php', headers={'Content-Type': data.content_type}, data=data.to_string(), timeout=60)
    resp.raise_for_status()
    result = resp.json()
    if result['success']:
        return 'https://a.pomf.cat/' + result['files'][0]['url']
    raise PomfUploadFail()
