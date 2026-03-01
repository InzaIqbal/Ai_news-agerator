"""
agents/digest_agent.py
Summarises videos and blog articles using the LLM.
"""

import json
from pydantic import BaseModel, field_validator
from agents.base_agent import BaseAgent
from database.connection import get_session
from database.repositories.video_repository import VideoRepository
from database.repositories.blog_repository import BlogRepository
import time 


class ContentSummary(BaseModel):
    clean_title: str
    summary: str

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 20:
            raise ValueError("Summary too short")
        return v.strip()

    @field_validator("clean_title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Title too short")
        return v.strip()


SYSTEM_PROMPT = """You are a senior AI journalist.
Given raw content, respond with ONLY valid JSON like this:
{
  "clean_title": "engaging title under 80 chars",
  "summary": "2-3 sentences explaining the content and why it matters to AI professionals"
}
No markdown fences. No extra text. Raw JSON only."""


class DigestAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.session    = get_session()
        self.video_repo = VideoRepository(self.session)
        self.blog_repo  = BlogRepository(self.session)

    def _summarise(self, raw_content: str, original_title: str) -> ContentSummary | None:
        user_prompt = (
            f"Original title: {original_title}\n\n"
            f"Content:\n{raw_content[:5000]}"
        )

        # Retry up to 3 times if rate limited
        for attempt in range(3):
            try:
                raw = self.chat(SYSTEM_PROMPT, user_prompt)
                raw = raw.strip()

                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]

                raw = raw.strip()
                data = json.loads(raw)
                return ContentSummary(**data)

            except Exception as e:
                if "429" in str(e):
                    wait = (attempt + 1) * 10  # wait 10s, 20s, 30s
                    print(f"   ⏳ Rate limited — waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    print(f"   ⚠️ Summarise error: {e}")
                    return None

        return None

    def run(self, *args, **kwargs) -> dict:
        print("\n🤖 [DigestAgent] Starting summarisation...")
        processed = 0

        videos = self.video_repo.get_unsummarised()
        print(f"   Videos to summarise: {len(videos)}")

        for v in videos:
            result = self._summarise(v.transcript or "", v.title)
            if result:
                self.video_repo.update_summary(
                    v.video_id, result.clean_title, result.summary
                )
                print(f"   ✅ {result.clean_title[:60]}")
                processed += 1
            time.sleep(3)

        articles = self.blog_repo.get_unsummarised()
        print(f"   Articles to summarise: {len(articles)}")

        for a in articles:
            result = self._summarise(a.content_md or "", a.title)
            if result:
                self.blog_repo.update_summary(
                    a.id, result.clean_title, result.summary
                )
                print(f"   ✅ {result.clean_title[:60]}")
                processed += 1
            time.sleep(3)

        print(f"   DigestAgent done. Processed: {processed}")
        return {"processed": processed}