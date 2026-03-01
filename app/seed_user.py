"""
seed_user.py
Run ONCE to create your user profile in the database.
Edit the details below to match your name, email, and interests.
"""

from database.connection import init_db, get_session
from database.repositories.digest_repository import UserRepository

init_db()

session = get_session()
repo    = UserRepository(session)

# ── Edit these to match YOU ────────────────────────
NAME        = "Inz Iqbal"
EMAIL       = "inzaiqbal912@gmail.com"
INTERESTS   = "AI agents, LLMs, OpenAI, Anthropic, Python, backend engineering, startup tech"
BACKGROUND  = "Software engineer building AI-powered products and multi-agent systems"
# ───────────────────────────────────────────────────

existing = repo.get_by_email(EMAIL)
if existing:
    print(f"✅ User already exists: {existing.name} ({existing.email})")
else:
    user = repo.create(NAME, EMAIL, INTERESTS, BACKGROUND)
    print(f"✅ Created user: {user.name} ({user.email})")

session.close()