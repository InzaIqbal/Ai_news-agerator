"""
agents/email_agent.py
Builds and sends the daily HTML digest email via Gmail SMTP.
"""

import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from agents.base_agent import BaseAgent
from config import EMAIL_USER, EMAIL_PASS, EMAIL_HOST, EMAIL_PORT
from database.connection import get_session
from database.repositories.video_repository import VideoRepository
from database.repositories.blog_repository import BlogRepository
from database.repositories.digest_repository import DigestRepository, UserRepository

load_dotenv()

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


class EmailAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.session     = get_session()
        self.video_repo  = VideoRepository(self.session)
        self.blog_repo   = BlogRepository(self.session)
        self.digest_repo = DigestRepository(self.session)
        self.user_repo   = UserRepository(self.session)
        self.jinja       = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR))
        )

    def _render_email(self, user_name: str, videos: list, articles: list) -> str:
        template = self.jinja.get_template("email_digest.html")
        return template.render(
            user_name=user_name,
            videos=videos,
            articles=articles,
            total=len(videos) + len(articles),
            date=datetime.utcnow().strftime("%A, %B %d %Y"),
        )

    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = EMAIL_USER
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
                server.login(EMAIL_USER, EMAIL_PASS)
                server.sendmail(EMAIL_USER, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"   ❌ Email error: {e}")
            return False

    def run(self, *args, **kwargs) -> bool:
        print("\n📧 [EmailAgent] Building digest...")

        users = self.user_repo.get_active_users()
        if not users:
            print("   ⚠️  No active users found.")
            return False

        user     = users[0]
        videos   = self.video_repo.get_top_unsent(limit=5)
        articles = self.blog_repo.get_top_unsent(limit=5)
        total    = len(videos) + len(articles)

        if total == 0:
            print("   ℹ️  No new content to send.")
            return False

        print(f"   📤 Sending to {user.email} ({total} items)...")
        html    = self._render_email(user.name, videos, articles)
        subject = f"🤖 Your AI News Digest — {datetime.utcnow().strftime('%b %d')}"
        digest  = self.digest_repo.create(user.id, total)
        success = self._send_email(user.email, subject, html)

        if success:
            self.digest_repo.mark_sent(digest.id)
            for v in videos:
                self.video_repo.mark_sent(v.video_id)
            for a in articles:
                self.blog_repo.mark_sent(a.id)
            print(f"   ✅ Email sent to {user.email}")
        else:
            self.digest_repo.mark_failed(digest.id)

        return success