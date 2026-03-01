"""
agents/curator_agent.py
Scores each summarised item against the user's interests.
Selects Top 10 across videos + articles.
"""

import json
from agents.base_agent import BaseAgent
from database.connection import get_session
from database.repositories.video_repository import VideoRepository
from database.repositories.blog_repository import BlogRepository
from database.repositories.digest_repository import UserRepository


SYSTEM_PROMPT = """You are a content curator for an AI professional.
Given the user's interests and background, rate how relevant this content is.
Respond with ONLY a JSON object: {"score": <float between 0.0 and 10.0>}
Higher = more relevant. Raw JSON only, no markdown."""


class CuratorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.session    = get_session()
        self.video_repo = VideoRepository(self.session)
        self.blog_repo  = BlogRepository(self.session)
        self.user_repo  = UserRepository(self.session)

    def _score_item(self, title: str, summary: str, interests: str, background: str) -> float:
        user_prompt = (
            f"User interests: {interests}\n"
            f"User background: {background}\n\n"
            f"Content title: {title}\n"
            f"Content summary: {summary}"
        )
        try:
            raw  = self.chat(SYSTEM_PROMPT, user_prompt, max_tokens=50)
            raw  = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            return float(data.get("score", 0.0))
        except Exception as e:
            print(f"   ⚠️ Score error: {e}")
            return 0.0

    def run(self) -> dict:
        print("\n🎯 [CuratorAgent] Scoring content...")

        users = self.user_repo.get_active_users()
        if not users:
            print("   ⚠️ No active users found. Add a user first via seed_user.py")
            return {"scored": 0}

        # Use first active user's profile for ranking
        user       = users[0]
        interests  = user.interests  or "AI, machine learning, LLMs, Python"
        background = user.background or "Software engineer interested in AI"

        scored = 0

        videos = self.video_repo.get_unscored()
        print(f"   Videos to score: {len(videos)}")
        for v in videos:
            score = self._score_item(v.clean_title or v.title, v.summary or "", interests, background)
            self.video_repo.update_score(v.video_id, score)
            print(f"   📊 Score {score:.1f} → {(v.clean_title or v.title)[:50]}")
            scored += 1

        articles = self.blog_repo.get_unscored()
        print(f"   Articles to score: {len(articles)}")
        for a in articles:
            score = self._score_item(a.clean_title or a.title, a.summary or "", interests, background)
            self.blog_repo.update_score(a.id, score)
            print(f"   📊 Score {score:.1f} → {(a.clean_title or a.title)[:50]}")
            scored += 1

        print(f"   CuratorAgent done. Scored: {scored}")
        return {"scored": scored}