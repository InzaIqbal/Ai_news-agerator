"""
database/repositories/blog_repository.py
All DB operations for BlogArticle.
"""

from typing import Optional
from sqlalchemy.orm import Session
from database.models import BlogArticle


class BlogRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Write ──────────────────────────────────────────────

    def save(self, article: BlogArticle) -> BlogArticle:
        existing = self.get_by_id(article.id)
        if existing:
            return existing
        self.session.add(article)
        self.session.commit()
        return article

    def update_summary(self, article_id: str, clean_title: str, summary: str) -> None:
        article = self.get_by_id(article_id)
        if article:
            article.clean_title = clean_title
            article.summary     = summary
            self.session.commit()

    def update_score(self, article_id: str, score: float) -> None:
        article = self.get_by_id(article_id)
        if article:
            article.score = score
            self.session.commit()

    def mark_sent(self, article_id: str) -> None:
        article = self.get_by_id(article_id)
        if article:
            article.is_sent = True
            self.session.commit()

    # ── Read ───────────────────────────────────────────────

    def get_by_id(self, article_id: str) -> Optional[BlogArticle]:
        return self.session.get(BlogArticle, article_id)

    def get_unsummarised(self) -> list[BlogArticle]:
        """Articles that have content but no summary yet."""
        return (
            self.session.query(BlogArticle)
            .filter(
                BlogArticle.content_md != None,
                BlogArticle.summary    == None,
            )
            .all()
        )

    def get_unscored(self) -> list[BlogArticle]:
        """Articles that have a summary but no score yet."""
        return (
            self.session.query(BlogArticle)
            .filter(
                BlogArticle.summary != None,
                BlogArticle.score   == 0.0,
            )
            .all()
        )

    def get_top_unsent(self, limit: int = 5) -> list[BlogArticle]:
        """Top ranked articles not yet sent in a digest."""
        return (
            self.session.query(BlogArticle)
            .filter(
                BlogArticle.is_sent  == False,
                BlogArticle.summary  != None,
            )
            .order_by(BlogArticle.score.desc())
            .limit(limit)
            .all()
        )
