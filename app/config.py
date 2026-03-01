"""
config.py
Central configuration — all constants and settings live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "ai_news")
DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# ── OpenRouter / OpenAI ───────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL", "openai/o1")

# ── Email ─────────────────────────────────────────────────
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_HOST = "smtp.gmail.com"        # ← add this
EMAIL_PORT = 465                     # ← add this

# ── User Profile (for email personalisation) ──────────────
USER_PROFILE = {
    "name":       "Inza Iqbal",
    "email":      os.getenv("EMAIL_USER"),
    "interests":  "AI agents, LLMs, OpenAI, Anthropic, Python, backend engineering",
    "background": "Software engineer building AI-powered products",
}

# ── YouTube Channels to Monitor ───────────────────────────
YOUTUBE_CHANNEL_IDS = {
    "Andrej Karpathy":   "UCXUPKJO5MZQN11PqgIvyuvQ",
    # "Yannic Kilcher":    "UCZHmQk67mSJgfCCTn7xBfew",
    # "Two Minute Papers": "UCbfYPyITQ-7l4upoX8nvctg",
    # "Lex Fridman":       "UCSHZKyawb77ixDdsGog4iWA",
    # "AI Explained":      "UCNJ1Ymd5yFuUPtn21xtRbbw",
    # "Sam Witteveen":     "UCyIe-61Y8C4_o-zZCtO4ETQ",
    # "TechWithTim":          "UC4JX40jDee_tINbkjycV4Sg",
}

# ── Blog RSS Feeds ────────────────────────────────────────
BLOG_SOURCES = {
    "OpenAI":          "https://openai.com/blog/rss.xml",
    # "Anthropic":       "https://www.anthropic.com/rss.xml",
    # "Google DeepMind": "https://deepmind.google/blog/rss.xml",
    # "Hugging Face":    "https://huggingface.co/blog/feed.xml",
    # "LangChain":       "https://blog.langchain.dev/rss/",
}

# ── Digest Settings ───────────────────────────────────────
MAX_VIDEOS_PER_DIGEST   = 5
MAX_ARTICLES_PER_DIGEST = 5