"""
database/models.py
All SQLAlchemy ORM models for the AI News Aggregator.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean,
    Integer, Float, ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ─── Content Tables ───────────────────────────────────────────────────────────

class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    video_id     = Column(String(20),  primary_key=True)
    title        = Column(String(500), nullable=False)
    url          = Column(String(200), nullable=False)
    channel      = Column(String(200))
    published_at = Column(DateTime)
    transcript   = Column(Text)           # raw transcript
    summary      = Column(Text)           # AI 2-3 sentence summary
    clean_title  = Column(String(500))    # AI-refined title
    score        = Column(Float, default=0.0)   # curator ranking score
    is_sent      = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<YouTubeVideo id={self.video_id} title={self.title[:40]}>"


class BlogArticle(Base):
    __tablename__ = "blog_articles"

    id           = Column(String(500), primary_key=True)  # URL used as PK
    title        = Column(String(500), nullable=False)
    url          = Column(String(500), nullable=False)
    source       = Column(String(200))    # "OpenAI" / "Anthropic" etc.
    published_at = Column(DateTime)
    content_md   = Column(Text)           # HTML → Markdown
    summary      = Column(Text)
    clean_title  = Column(String(500))
    score        = Column(Float, default=0.0)
    is_sent      = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<BlogArticle source={self.source} title={self.title[:40]}>"


# ─── User / Digest Tables ─────────────────────────────────────────────────────

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(200), nullable=False)
    email       = Column(String(200), nullable=False, unique=True)
    interests   = Column(Text)   # e.g. "AI, LLMs, Python, startups"
    background  = Column(Text)   # e.g. "ML engineer building AI products"
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    digests = relationship("Digest", back_populates="user")

    def __repr__(self):
        return f"<UserProfile name={self.name} email={self.email}>"


class Digest(Base):
    __tablename__ = "digests"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("user_profiles.id"))
    sent_at     = Column(DateTime)
    item_count  = Column(Integer, default=0)
    status      = Column(String(50), default="pending")  # pending|sent|failed
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserProfile", back_populates="digests")

    def __repr__(self):
        return f"<Digest user_id={self.user_id} status={self.status}>"