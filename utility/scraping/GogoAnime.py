import json
import urllib.parse
import bs4
import urllib.request
import urllib.parse
from Crypto.Cipher import AES  # pycryptodome
import base64
import re
import httpx
from utility.common import decorators
from utility.common import config
from utility.common.requests import get_redirect_url
from urllib.parse import quote
from dataclasses import dataclass, field


client = httpx.AsyncClient()


class AesCbc:
    """
        Encryption and decryption using AES CBC
    """
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv
        self.mode = AES.MODE_CBC
        self.size = AES.block_size
        self.pad = lambda s: s + (self.size - len(s) % self.size) * chr(self.size - len(s) % self.size)

    def encrypt(self, content: str) -> bytes:
        """
            Encrypts the content
        """
        cryptor = AES.new(self.key, self.mode, self.iv)
        encrypted = cryptor.encrypt(str.encode(self.pad(content)))
        return base64.b64encode(encrypted)

    def decrypt(self, content: str) -> str:
        """
            Decrypts the content with no padding
        """
        cryptor = AES.new(self.key, self.mode, self.iv)
        content += (len(content) % 4) * '='
        content = base64.b64decode(content)
        decrypted = cryptor.decrypt(content)
        return re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\n\r\t]').sub('', decrypted.decode())

async def _get_values(url):
    """
        Gets the different values needed for getting the stream url
    """
    resp = await client.get(url)  # gets the episode document
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)
    div = soup.select_one('div.anime_video_body_watch_items.load')
    div = div.select_one('div') # gets the div inside the div
    iframe = div.select_one('iframe')  # gets the element "iframe" inside the div
    src = iframe.attrs['src']  # gets the source from the iframe element
    player = 'https:' + src

    resp = await client.get(player)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)

    iv = soup.select_one('div.wrapper').attrs['class'][1].split('container-')[1].encode()
    secret_key = soup.select_one('body[class]').attrs['class'][0].split('container-')[1].encode()
    decryption_key = soup.select_one('div.videocontent').attrs['class'][1].split('videocontent-')[1].encode()
    
    data_value = soup.select_one('script[data-value]').attrs['data-value']
    
    crypto_handler = AesCbc(secret_key, iv)
    encrypt_ajax_params = crypto_handler.decrypt(data_value)
    encrypt_ajax_params = '&'.join(encrypt_ajax_params.split('&')[1:])

    return player, iv, secret_key, decryption_key, encrypt_ajax_params

#@decorators.Async.logging.log
async def video_from_url(url):
    """
        Gets the stream url to an anime from the GogoAnime website
    """
    player, iv, secret_key, decryption_key, encrypt_ajax_params = await _get_values(url)

    http_url = urllib.parse.urlparse(player)
    host = 'https://' + http_url.hostname + '/'
    ID = urllib.parse.parse_qs(http_url.query)['id'][0]
    
    crypto_handler = AesCbc(secret_key, iv)
    encrypted_id = crypto_handler.encrypt(ID).decode()

    final_url = f'{host}encrypt-ajax.php?id={encrypted_id}&{encrypt_ajax_params}&alias={ID}'
    
    async with httpx.AsyncClient(headers={'X-Requested-With': 'XMLHttpRequest'}) as client:
        resp = await client.get(final_url)
        resp.raise_for_status()
    
    crypto_handler = AesCbc(decryption_key, iv)
    
    data = resp.json()['data']
    decrypted_data = crypto_handler.decrypt(data)
    
    data = json.loads(decrypted_data)

    source = data['source'][0]
    file_url = source['file']

    return file_url

@dataclass(frozen=True, kw_only=True)
class AnimeItem:
    title: str = field(repr=True, compare=False)
    release: str = field(repr=False, compare=False)
    path: str = field(repr=False, compare=True)
    url: str = field(repr=False, compare=False)
    thumbnail: str = field(repr=False, compare=False)


def __parse_anime_data(anime: bs4.element.Tag, base_url: str) -> AnimeItem:
    kwargs = {
        'title': anime.select_one('p.name a').attrs['title'],
        'release': anime.select_one('p.released').text.strip(),
        'path': anime.select_one('p.name a').attrs['href'],
        'thumbnail': anime.select_one('div.img a img').attrs['src']
    }
    kwargs['url'] =  base_url.rstrip('/') + kwargs['path']
    return AnimeItem(**kwargs)
    
def _parse_search_doc(doc: bytes, base_url: str) -> list[AnimeItem]:
    soup = bs4.BeautifulSoup(doc, features=config.bs4.parser)
    animes = soup.select('ul.items li')
    results = [__parse_anime_data(anime, base_url) for anime in animes]
    return results

async def search(query: str) -> list[AnimeItem]:
    base_url = await get_redirect_url(config.gogo.base_url)
    search_url = f'{base_url}/search.html?keyword={quote(query)}'
    
    resp = await client.get(search_url)
    resp.raise_for_status()
    
    search_results = _parse_search_doc(resp.content, base_url)
        
    return search_results

@dataclass(frozen=True, kw_only=True)
class EpisodeItem:
    path: str = field(repr=True, compare=True)
    url: str = field(repr=False, compare=False)
    number: int = field(repr=False, compare=False)


def __parse_episode_data(element: bs4.element.Tag, base_url: str) -> EpisodeItem:
    kwargs = {
        'path': element.select_one('a').attrs['href'].lstrip(),
        'number': int(element.select_one('div.name').contents[1].lstrip())
    }
    kwargs['url'] = base_url.rstrip('/') + kwargs['path']
    return EpisodeItem(**kwargs)


async def _get_episodes_ajax(total_episodes: str, ID: str, base_url: str) -> list[EpisodeItem]:
    resp = await client.get(f'https://ajax.gogo-load.com/ajax/load-list-episode?ep_start=0&ep_end={total_episodes}&id={ID}')
    resp.raise_for_status()
    
    soup = bs4.BeautifulSoup(resp.content, features=config.bs4.parser)
    episodes = soup.select('ul#episode_related li')
    return [__parse_episode_data(episode, base_url) for episode in episodes]

async def _parse_episode_list(doc: bytes, base_url: str):
    soup = bs4.BeautifulSoup(doc, features=config.bs4.parser)
    
    total_episodes = soup.select_one('ul#episode_page li a.active').attrs['ep_end']
    ID = soup.select_one('input#movie_id').attrs['value']
    return await _get_episodes_ajax(total_episodes, ID, base_url)

async def get_episodes(url: str) -> list[EpisodeItem]:
    resp = await client.get(url)
    resp.raise_for_status()
    base_url = 'https://' + urllib.parse.urlparse(url).hostname
    episodes = await _parse_episode_list(resp.content, base_url)
    return episodes[::-1]
    
