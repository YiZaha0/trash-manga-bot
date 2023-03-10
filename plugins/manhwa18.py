import re

from typing import List, AsyncIterable
from urllib.parse import urlparse, urljoin, quote_plus

from bs4 import BeautifulSoup

from plugins.client import MangaClient, MangaCard, MangaChapter, LastChapter


class Manhwa18Client(MangaClient):

    base_url = urlparse("https://manhwa18.cc/")
    search_url = urljoin(base_url.geturl(), "search")
    search_param = "q"

    pre_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }

    def __init__(self, *args, name="Manhwa18", **kwargs):
        super().__init__(*args, name=name, headers=self.pre_headers, **kwargs)

    def mangas_from_page(self, page: bytes):
        bs = BeautifulSoup(page, "html.parser")

        cards = bs.findAll("div", {"class": "manga-item"})

        mangas = [card.findNext("h3").findNext("a") for card in cards]
        names = [manga.string.strip() for manga in mangas]
        url = [urljoin(self.base_url.geturl(), manga.get('href')) for manga in mangas]

        images = [card.findNext('img').get('src') for card in cards]

        mangas = [MangaCard(self, *tup) for tup in zip(names, url, images)]

        return mangas

    def chapters_from_page(self, page: bytes, manga: MangaCard = None):
        bs = BeautifulSoup(page, "html.parser")

        ul = bs.find("div", {"class": "panel-manga-chapter wleft"})

        items = ul.findAll("a")

        links = [urljoin(self.base_url.geturl(), item.get('href')) for item in items]
        texts: List[str] = [item.string.strip() for item in items]

        return list(map(lambda x: MangaChapter(self, x[0], x[1], manga, []), zip(texts, links)))

    def updates_from_page(self, content: bytes):
        bs = BeautifulSoup(content, "html.parser")

        container = bs.find("div", {"class": "manga-lists"})
        
        items = bs.findAll("div", {"class": "data wleft"})

        urls = dict()

        for item in items:
            manga_url = urljoin(self.base_url.geturl(), item.findNext('a').get('href'))

            if manga_url in urls:
                continue 

            chapter_item = item.findNext("div", {"class": "chapter-item wleft"})
            
            chapter_url = urljoin(self.base_url.geturl(), chapter_item.find("a").get("href"))

            urls[manga_url] = chapter_url

        return urls

    async def pictures_from_chapters(self, content: bytes, response=None):
        bs = BeautifulSoup(content, "html.parser")

        image_items = bs.findAll("img", {"class": re.compile("p*")})

        images_url = [image_item.get("src") for image_item in image_items]

        return images_url 
        
    async def get_picture(self, manga_chapter: MangaChapter, url, *args, **kwargs):
        headers = dict(self.headers)
        headers['Referer'] = self.base_url.geturl() 
        
        return await super(Manhwa18Client, self).get_picture(manga_chapter, url, headers=headers, *args, **kwargs)

    async def search(self, query: str = "", page: int = 1) -> List[MangaCard]:
        query = quote_plus(query)

        request_url = f'{self.search_url}'

        if query:
            request_url += f'?{self.search_param}={query}'

        content = await self.get_url(request_url)

        return self.mangas_from_page(content)

    async def get_chapters(self, manga_card: MangaCard, page: int = 1) -> List[MangaChapter]:

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        return self.chapters_from_page(content, manga_card)[(page - 1) * 20:page * 20]

    async def iter_chapters(self, manga_url: str, manga_name) -> AsyncIterable[MangaChapter]:
        manga_card = MangaCard(self, manga_name, manga_url, '')

        request_url = f'{manga_card.url}'

        content = await self.get_url(request_url)

        for chapter in self.chapters_from_page(content, manga_card):
            yield chapter

    async def contains_url(self, url: str):
        return url.startswith(self.base_url.geturl())

    async def check_updated_urls(self, last_chapters: List[LastChapter]):

        content = await self.get_url(self.base_url.geturl())

        updates = self.updates_from_page(content)

        updated = [lc.url for lc in last_chapters if updates.get(lc.url) and updates.get(lc.url) != lc.chapter_url]
        not_updated = [lc.url for lc in last_chapters if
                       not updates.get(lc.url) or updates.get(lc.url) == lc.chapter_url]

        return updated, not_updated
