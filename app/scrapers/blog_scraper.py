"""
scrapers/blog_scraper.py
"""

from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import html2text
import requests
from bs4 import BeautifulSoup

from config import BLOG_SOURCES
from database.connection import get_session
from database.models import BlogArticle
from database.repositories.blog_repository import BlogRepository
from scrapers.base_scraper import BaseScraper

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AINewsBot/1.0)"}


def html_to_markdown(html: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links  = False
    h.ignore_images = True
    h.body_width    = 0
    return h.handle(html)


def fetch_full_content(url: str) -> str:
    try:
        resp    = requests.get(url, headers=HEADERS, timeout=15)
        soup    = BeautifulSoup(resp.text, "html.parser")
        article = soup.find("article") or soup.find("main") or soup.body
        return html_to_markdown(str(article))[:10000]
    except Exception as e:
        print(f"   ⚠️  Content fetch failed: {e}")
        return ""


class BlogScraper(BaseScraper):

    def __init__(self):
        self.session = get_session()
        self.repo    = BlogRepository(self.session)

    def fetch_metadata(self) -> list[dict]:
        articles = []
        for source_name, rss_url in BLOG_SOURCES.items():
            print(f"   📡 Fetching: {source_name}")
            try:
                feed = feedparser.parse(rss_url)
            except Exception as e:
                print(f"   ⚠️  {source_name} RSS failed: {e}")
                continue

            for entry in feed.entries[:10]:
                url   = entry.get("link", "")
                title = entry.get("title", "")
                if not url or not title:
                    continue

                content_html = ""
                if entry.get("content"):
                    content_html = entry.content[0].value
                elif entry.get("summary"):
                    content_html = entry.summary

                content_md = (
                    html_to_markdown(content_html)[:10000]
                    if content_html
                    else fetch_full_content(url)
                )

                published_at = None
                if entry.get("published"):
                    try:
                        published_at = parsedate_to_datetime(entry.published)
                    except Exception:
                        published_at = datetime.utcnow()

                articles.append({
                    "id":           url,
                    "title":        title,
                    "url":          url,
                    "source":       source_name,
                    "published_at": published_at,
                    "content_md":   content_md,
                })
        return articles

    def save_to_db(self, items: list[dict]) -> int:
        new_count = 0
        for item in items:
            saved = self.repo.save(BlogArticle(**item))
            if saved.id == item["id"]:
                new_count += 1
        return new_count