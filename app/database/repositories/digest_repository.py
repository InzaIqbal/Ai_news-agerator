"""
database/repositories/digest_repository.py
DB operations for Digest and UserProfile.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Digest, UserProfile


class DigestRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, item_count: int) -> Digest:
        digest = Digest(user_id=user_id, item_count=item_count)
        self.session.add(digest)
        self.session.commit()
        return digest

    def mark_sent(self, digest_id: int) -> None:
        digest = self.session.get(Digest, digest_id)
        if digest:
            digest.status  = "sent"
            digest.sent_at = datetime.utcnow()
            self.session.commit()

    def mark_failed(self, digest_id: int) -> None:
        digest = self.session.get(Digest, digest_id)
        if digest:
            digest.status = "failed"
            self.session.commit()


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_active_users(self) -> list[UserProfile]:
        return (
            self.session.query(UserProfile)
            .filter(UserProfile.is_active == True)
            .all()
        )

    def get_by_email(self, email: str) -> Optional[UserProfile]:
        return (
            self.session.query(UserProfile)
            .filter(UserProfile.email == email)
            .first()
        )

    def create(self, name: str, email: str, interests: str, background: str) -> UserProfile:
        user = UserProfile(
            name=name,
            email=email,
            interests=interests,
            background=background,
        )
        self.session.add(user)
        self.session.commit()
        return user