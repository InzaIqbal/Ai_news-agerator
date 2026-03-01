"""
scrapers/youtube_scraper.py
Scrapes YouTube RSS feeds and fetches transcripts using Webshare proxy.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import feedparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)
from youtube_transcript_api.proxies import WebshareProxyConfig

from config import YOUTUBE_CHANNEL_IDS
from database.connection import get_session
from database.models import YouTubeVideo
from database.repositories.video_repository import VideoRepository
from scrapers.base_scraper import BaseScraper

RSS_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

# Skip these types of videos
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

        # ── Setup Webshare Proxy ───────────────────────────
        proxy_username = os.getenv("PROXY_USERNAME")
        proxy_password = os.getenv("PROXY_PASSWORD")

        if proxy_username and proxy_password:
            proxy_config = WebshareProxyConfig(
                proxy_username=proxy_username,
                proxy_password=proxy_password,
            )
            self.transcript_api = YouTubeTranscriptApi(proxy_config=proxy_config)
            print("   🔐 Using Webshare proxy for transcripts")
        else:
            self.transcript_api = YouTubeTranscriptApi()
            print("   ⚠️  No proxy configured — transcripts may be blocked")

    def fetch_metadata(self) -> list[dict]:
        """Fetch recent videos (last 168 hours / 7 days) from all channels."""
        videos = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=168)

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
        new_count = 0
        for item in items:
            saved = self.repo.save(YouTubeVideo(**item))
            if saved.video_id == item["video_id"]:
                new_count += 1
        return new_count

    def get_transcript(self, video_id: str) -> dict:
        """
        Fetch transcript via proxy-enabled API instance.
        Uses .text attribute (not ['text']) on snippet objects.
        """
        try:
            transcript = self.transcript_api.fetch(video_id)
            text = " ".join(snippet.text for snippet in transcript.snippets)
            return {
                "status": "available",
                "text":   text[:8000],
                "error":  None
            }
        except NoTranscriptFound:
            return {"status": "unavailable", "text": None, "error": "No transcript found"}
        except TranscriptsDisabled:
            return {"status": "unavailable", "text": None, "error": "Transcripts disabled"}
        except VideoUnavailable:
            return {"status": "unavailable", "text": None, "error": "Video unavailable"}
        except Exception as e:
            return {"status": "unavailable", "text": None, "error": str(e)}

    def fetch_transcripts(self) -> None:
        """Fetch transcripts for 5 most recent videos using proxy."""
        videos = (
            self.session.query(YouTubeVideo)
            .filter(YouTubeVideo.transcript == None)
            .order_by(YouTubeVideo.published_at.desc())
            .limit(5)                               # ✅ only 5 videos
            .all()
        )

        if not videos:
            print("   📝 No new videos need transcripts.")
            return

        print(f"   📝 Fetching transcripts for {len(videos)} videos...")
        success_count = 0

        for i, video in enumerate(videos, 1):
            print(f"   [{i}/{len(videos)}] {video.title[:55]}")
            result = self.get_transcript(video.video_id)

            if result["status"] == "available":
                self.repo.update_transcript(video.video_id, result["text"])
                print(f"   ✅ Transcript saved ({len(result['text'])} chars)")
                success_count += 1
            else:
                print(f"   ⚠️  No transcript: {result['error']}")

            time.sleep(2)   # small delay between requests

        print(f"   📊 {success_count}/{len(videos)} transcripts fetched")

    def run(self) -> int:
        count = super().run()
        self.fetch_transcripts()
        return count