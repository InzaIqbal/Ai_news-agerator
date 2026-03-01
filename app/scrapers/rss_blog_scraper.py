import feedparser
import httpx
from bs4 import BeautifulSoup
import html2text
from .base_scraper import BaseScraper


class RSSBlogScraper(BaseScraper):

    def __init__(self, name: str, rss_url: str):
        self.name = name
        self.rss_url = rss_url

    def fetch(self):
        feed = feedparser.parse(self.rss_url)
        articles = []

        for entry in feed.entries:
            articles.append({
                "source": self.name,
                "title": entry.title,
                "url": entry.link,
                "published": entry.get("published", None)
            })

        return articles

    async def fetch_full_content(self, url: str):
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url)
            html = response.text
            return self.clean_html(html)

    def clean_html(self, html: str):
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts and styles
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return str(soup)

    def html_to_markdown(self, html: str):
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0
        return converter.handle(html)