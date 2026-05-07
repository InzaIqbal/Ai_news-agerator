"""
scrapers/youtube_scraper.py
Scrapes YouTube RSS feeds and fetches transcripts using yt-dlp (FREE).
No proxy needed. No API key needed.
"""

import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser

from config import YOUTUBE_CHANNEL_IDS
from database.connection import get_session
from database.models import YouTubeVideo
from database.repositories.video_repository import VideoRepository
from scrapers.base_scraper import BaseScraper
from services.transcript_fetcher import get_transcript   # new yt-dlp fetcher

RSS_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

SKIP_KEYWORDS = [
    "livestream", "live stream", "live podcast", "sunday",
    "stream", "gsap", "svg", "raw dogging", "holiday", "x-mas"
]


def is_short(title: str) -> bool:
    return any(kw in title.lower() for kw in ["#shorts", "#short", "shorts"])


def is_skippable(title: str) -> bool:
    return any(kw in title.lower() for kw in SKIP_KEYWORDS)


class YouTubeScraper(BaseScraper):

    def __init__(self):
        self.session = get_session()
        self.repo    = VideoRepository(self.session)
        # No proxy setup needed — yt-dlp handles everything for free!

    def fetch_metadata(self) -> list[dict]:
        """Fetch recent videos (last 7 days) from all configured channels."""
        videos = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=720)

        for channel_name, channel_id in YOUTUBE_CHANNEL_IDS.items():
            print(f"   📡 Fetching: {channel_name}")
            url  = RSS_TEMPLATE.format(channel_id=channel_id)
            feed = feedparser.parse(url)

            for entry in feed.entries:
                video_id = entry.get("yt_videoid", "")
                title    = entry.get("title", "")

                if not video_id:
                    continue
                if is_short(title):
                    continue
                if is_skippable(title):
                    continue

                published_at = None
                if entry.get("published"):
                    try:
                        published_at = parsedate_to_datetime(entry.published)
                        if published_at < cutoff:
                            continue
                    except Exception:
                        published_at = datetime.now(timezone.utc)

                videos.append({
                    "video_id":     video_id,
                    "title":        title,
                    "url":          f"https://www.youtube.com/watch?v={video_id}",
                    "channel":      channel_name,
                    "published_at": published_at,
                })

        return videos

    def save_to_db(self, items: list[dict]) -> int:
        """Save new videos to DB. Returns count of truly new items."""
        new_count = 0
        for item in items:
            existing = self.repo.get_by_id(item["video_id"])
            if not existing:
                self.repo.save(YouTubeVideo(**item))
                new_count += 1
        return new_count

    def fetch_transcripts(self) -> None:
        """Fetch transcripts using yt-dlp — free, no proxy, no API key."""
        videos = (
            self.session.query(YouTubeVideo)
            .filter(YouTubeVideo.transcript == None)
            .order_by(YouTubeVideo.published_at.desc())
            .limit(5)
            .all()
        )

        if not videos:
            print("   📝 No new videos need transcripts.")
            return

        print(f"   📝 Fetching transcripts for {len(videos)} videos...")
        success_count = 0

        for i, video in enumerate(videos, 1):
            print(f"\n   [{i}/{len(videos)}] {video.title[:60]}")
            result = get_transcript(video.video_id)

            if result["status"] == "available":
                self.repo.update_transcript(video.video_id, result["text"])
                print(f"   ✅ Saved ({len(result['text'])} chars) via {result['method']}")
                success_count += 1
            else:
                print(f"   ⚠️  Skipped: {result['error']}")

            time.sleep(2)

        print(f"\n   📊 {success_count}/{len(videos)} transcripts fetched successfully")

    def run(self) -> int:
        count = super().run()
        self.fetch_transcripts()
        return count