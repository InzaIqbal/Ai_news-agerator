"""
scrapers/base_scraper.py
Abstract base class all scrapers must implement.
"""

from abc import ABC, abstractmethod


class BaseScraper(ABC):

    @abstractmethod
    def fetch_metadata(self) -> list[dict]:
        """Fetch metadata from the source. Returns list of dicts."""
        ...

    @abstractmethod
    def save_to_db(self, items: list[dict]) -> int:
        """Save items to DB. Returns count of NEW items saved."""
        ...

    def run(self) -> int:
        """Full pipeline: fetch → save. Returns new item count."""
        print(f"🔍 [{self.__class__.__name__}] Fetching...")
        items = self.fetch_metadata()
        print(f"   Found {len(items)} items")
        new_count = self.save_to_db(items)
        print(f"   ✅ Saved {new_count} new items")
        return new_count