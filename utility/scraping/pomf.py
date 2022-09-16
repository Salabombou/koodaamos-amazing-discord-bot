import httpx
from requests_toolbelt import MultipartEncoder
from utility.common.errors import PomfUploadFail
from utility.common.file_management import get_bytes

client = httpx.AsyncClient(timeout=300)

async def upload(file, ctx):
    file = await get_bytes(file)
    filesize = len(file)
    filesize_limit = ctx.guild.filesize_limit
    if not filesize < 75 * 1000 * 1000 or filesize < filesize_limit:
        return ''
    fields = {
        'files[]': ('video.mp4', file, 'video/mp4')
    }
    data = MultipartEncoder(fields=fields)
    resp = await client.post(url='https://pomf.cat/upload.php', headers={'Content-Type': data.content_type}, data=data.to_string(), timeout=60)
    resp.raise_for_status()
    result = resp.json()
    if result['success']:
        return 'https://a.pomf.cat/' + result['files'][0]['url']
    raise PomfUploadFail()
