import json
import urllib.parse
import bs4
import urllib.request
import urllib.parse
from Crypto.Cipher import AES # pycryptodome
import base64
import re
import httpx

client = httpx.AsyncClient()
    
class AesCbc:
    def __init__(self, key=None):
        self.key = key
        self.mode = AES.MODE_CBC
        self.size = AES.block_size
        self.pad = lambda s: s + (self.size - len(s) % self.size) * chr(self.size - len(s) % self.size)

    def encrypt(self, content, iv):
        cryptor = AES.new(self.key, self.mode, iv)
        encrypted = cryptor.encrypt(str.encode(self.pad(content)))
        return base64.b64encode(encrypted)
    
    def decrypt(self, content, iv):
        cryptor = AES.new(self.key, self.mode, iv)
        content += (len(content) % 4) * '='
        content = base64.b64decode(content)
        decrypted = cryptor.decrypt(content)
        return re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', decrypted.decode())

def crypto_handler(data_value, iv, secret_key, encrypt=True):
    secret_key = str.encode(secret_key)
    iv = str.encode(iv)
    thingy = AesCbc(key=secret_key)
    if not encrypt:
        decrypted = thingy.decrypt(data_value, iv)
        return decrypted
    else:
        encrypted = thingy.encrypt(data_value, iv)
        return encrypted

def substring_after(string, sub):
    string = string.split(sub)[1:]
    string = sub.join(string)
    return string

async def get_values(url):
    resp = await client.get(url) # gets the episode document
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features='lxml') # soup
    div = soup.find('div', {'class': 'anime_video_body_watch_items load'}) # gets the div
    div = div.find('div') # gets the div inside the div
    iframe = div.find('iframe') # gets the element "iframe" inside the div
    src = iframe['src'] # gets the source from the iframe element
    player = 'https:' + src

    resp = await client.get(player)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features='lxml')

    iv = soup.select('div.wrapper')[0]['class'][1].split('container-')[1]
    secret_key = soup.select('body[class]')[0]['class'][0].split('container-')[1]
    decryption_key = soup.select('div.videocontent')[0]['class'][1].split('videocontent-')[1]

    data_value = soup.select('script[data-value]')[0]['data-value']
    encrypt_ajax_params = crypto_handler(data_value, iv, secret_key, False)
    encrypt_ajax_params = substring_after(encrypt_ajax_params, '&')

    return player, iv, secret_key, decryption_key, encrypt_ajax_params

async def video_from_url(url):
    player, iv, secret_key, decryption_key, encrypt_ajax_params = await get_values(url)

    http_url = urllib.parse.urlparse(player)
    host = 'https://' + http_url.hostname + '/'
    ID = urllib.parse.parse_qs(http_url.query)['id'][0]

    encrypted_id = crypto_handler(ID, iv, secret_key).decode('utf-8')

    final_url = f'{host}encrypt-ajax.php?id={encrypted_id}&{encrypt_ajax_params}&alias={ID}'
    resp = await httpx.AsyncClient(headers={'X-Requested-With': 'XMLHttpRequest'}).get(final_url)
    resp.raise_for_status()
        
    data = resp.json()['data']
    decrypted_data = crypto_handler(data, iv, decryption_key, False)
    data = json.loads(decrypted_data)
        
    source = data['source'][0]
    file_url = source['file']

    return file_url
    