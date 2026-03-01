"""
database/repositories/video_repository.py
All DB operations for YouTubeVideo.
"""

from typing import Optional
from sqlalchemy.orm import Session
from database.models import YouTubeVideo


class VideoRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Write ──────────────────────────────────────────────

    def save(self, video: YouTubeVideo) -> YouTubeVideo:
        existing = self.get_by_id(video.video_id)
        if existing:
            return existing
        self.session.add(video)
        self.session.commit()
        return video

    def update_transcript(self, video_id: str, transcript: str) -> None:
        video = self.get_by_id(video_id)
        if video:
            video.transcript = transcript
            self.session.commit()

    def update_summary(self, video_id: str, clean_title: str, summary: str) -> None:
        video = self.get_by_id(video_id)
        if video:
            video.clean_title = clean_title
            video.summary     = summary
            self.session.commit()

    def update_score(self, video_id: str, score: float) -> None:
        video = self.get_by_id(video_id)
        if video:
            video.score = score
            self.session.commit()

    def mark_sent(self, video_id: str) -> None:
        video = self.get_by_id(video_id)
        if video:
            video.is_sent = True
            self.session.commit()

    # ── Read ───────────────────────────────────────────────

    def get_by_id(self, video_id: str) -> Optional[YouTubeVideo]:
        return self.session.get(YouTubeVideo, video_id)

    def get_unsummarised(self) -> list[YouTubeVideo]:
        return (
            self.session.query(YouTubeVideo)
            .filter(
                YouTubeVideo.transcript != None,
                YouTubeVideo.summary    == None,
            )
            .all()
        )

    def get_unscored(self) -> list[YouTubeVideo]:
        return (
            self.session.query(YouTubeVideo)
            .filter(
                YouTubeVideo.summary != None,
                YouTubeVideo.score   == 0.0,
            )
            .all()
        )

    def get_top_unsent(self, limit: int = 5) -> list[YouTubeVideo]:
        return (
            self.session.query(YouTubeVideo)
            .filter(
                YouTubeVideo.is_sent  == False,
                YouTubeVideo.summary  != None,
            )
            .order_by(YouTubeVideo.score.desc())
            .limit(limit)
            .all()
        )

