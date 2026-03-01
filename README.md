# 🤖 AI News Aggregator

An automated AI-powered news aggregator that scrapes YouTube channels and top AI blogs, summarises content using LLMs, ranks it based on your personal interests, and delivers a beautiful daily email digest — all on autopilot.

---

## 📸 What You Get

Every day, you receive a professional HTML email digest containing:
- 📰 Top AI blog articles from OpenAI, Anthropic, Google DeepMind, HuggingFace & LangChain
- 🎥 Latest YouTube videos from top AI educators and researchers
- 🤖 AI-generated summaries (2-3 sentences each)
- ⭐ Relevance scores based on YOUR interests and background
- 🔗 Direct links to read/watch

---

## 🏗️ Architecture

```
YouTube RSS Feeds ──┐
                    ├──▶ PostgreSQL DB ──▶ DigestAgent ──▶ CuratorAgent ──▶ EmailAgent ──▶ Gmail
Blog RSS Feeds  ────┘    (store raw)       (summarise)      (rank 0-10)     (send HTML)
```

### Multi-Agent Pipeline

| Step | Agent | What it does |
|------|-------|-------------|
| 1 | YouTubeScraper | Fetches video metadata from RSS feeds |
| 2 | BlogScraper | Fetches full articles from RSS feeds |
| 3 | DigestAgent | Summarises content using LLM (2-3 sentences) |
| 4 | CuratorAgent | Scores each item 0-10 based on your interests |
| 5 | EmailAgent | Renders HTML template and sends via Gmail SMTP |

---

## 🗂️ Project Structure

```
ai-news-aggregator/
├── agents/
│   ├── base_agent.py          # OpenRouter client setup
│   ├── digest_agent.py        # LLM summarisation
│   ├── curator_agent.py       # Personalised ranking
│   └── email_agent.py         # HTML email builder + SMTP sender
├── scrapers/
│   ├── base_scraper.py        # Abstract base class
│   ├── youtube_scraper.py     # RSS feeds + transcript fetching
│   └── blog_scraper.py        # RSS + HTML→Markdown conversion
├── database/
│   ├── models.py              # SQLAlchemy ORM models
│   ├── connection.py          # Engine + session factory
│   └── repositories/
│       ├── video_repository.py
│       ├── blog_repository.py
│       ├── digest_repository.py
│       └── user_repository.py
├── templates/
│   └── email_digest.html      # Jinja2 HTML email template
├── main.py                    # Pipeline orchestrator
├── seed_user.py               # One-time user profile setup
├── config.py                  # All settings and constants
├── requirements.txt
└── .env                       # Your secrets (never commit this!)
```

---

## ⚙️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.11+ | Core language |
| PostgreSQL 17 | Database |
| SQLAlchemy 2.0 | ORM |
| OpenRouter API | LLM access (OpenAI-compatible) |
| feedparser | RSS feed parsing |
| html2text | HTML → Markdown conversion |
| Jinja2 | HTML email templating |
| Gmail SMTP | Email delivery |
| youtube-transcript-api | YouTube transcript fetching |
| Webshare Proxies | Bypass YouTube IP blocks |
| Pydantic | Data validation |

---

## 🚀 Setup Guide

### Prerequisites

- Python 3.11+
- PostgreSQL 17
- Gmail account with App Password enabled
- OpenRouter API key (free at openrouter.ai)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/ai-news-aggregator.git
cd ai-news-aggregator
```

---

### Step 2 — Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4 — Create PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE ai_news;"
```

Or in pgAdmin: right-click Databases → Create → Database → name it `ai_news`

---

### Step 5 — Configure environment variables

Create a `.env` file in the `app/` folder:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ai_news
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# OpenRouter (get free API key at openrouter.ai)
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-oss-120b:free

# Gmail (use App Password, not your real password)
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=your-gmail-app-password

# Webshare Proxy (optional — needed for YouTube transcripts)
PROXY_USERNAME=your-webshare-username
PROXY_PASSWORD=your-webshare-password
```

---

### Step 6 — Get a Gmail App Password

1. Go to **myaccount.google.com**
2. Click **Security**
3. Enable **2-Step Verification**
4. Search for **App Passwords**
5. Create new → name it "AI News Bot"
6. Copy the 16-character password into `.env`

---

### Step 7 — Get OpenRouter API Key

1. Go to **openrouter.ai**
2. Sign up for free
3. Go to **API Keys** → Create new key
4. Copy into `.env`
5. Recommended free model: `openai/gpt-oss-120b:free`

---

### Step 8 — Seed your user profile

```bash
cd app
python seed_user.py
```

You should see:
```
✅ Database tables created / verified.
✅ Created user: Your Name (youremail@gmail.com)
```

---

### Step 9 — Run the pipeline!

```bash
python main.py
```

Test without sending email:
```bash
python main.py --no-email
```

---

## 📡 Monitored Sources

### YouTube Channels

| Channel | Focus |
|---------|-------|
| Andrej Karpathy | Deep learning, LLMs |
| Yannic Kilcher | AI paper reviews |
| Two Minute Papers | Research summaries |
| Lex Fridman | AI interviews |
| AI Explained | AI news & trends |
| Sam Witteveen | LLM engineering |

### Blog Sources

| Blog | Focus |
|------|-------|
| OpenAI Blog | GPT, ChatGPT updates |
| Anthropic Blog | Claude, AI safety |
| Google DeepMind | Research breakthroughs |
| Hugging Face | Open source AI tools |
| LangChain Blog | AI agents & frameworks |

---

## 🗃️ Database Models

### YouTubeVideo
```
video_id      PK  — YouTube video ID
title             — Original title
channel           — Channel name
url               — Watch URL
published_at      — Publication date
transcript        — Full transcript text (if available)
clean_title       — AI-generated clean title
summary           — AI-generated 2-3 sentence summary
score             — Relevance score 0-10
is_sent           — Whether included in a digest
```

### BlogArticle
```
id            PK  — Article URL (unique)
title             — Original title
source            — Blog name
url               — Article URL
published_at      — Publication date
content_md        — Full content as Markdown
clean_title       — AI-generated clean title
summary           — AI-generated 2-3 sentence summary
score             — Relevance score 0-10
is_sent           — Whether included in a digest
```

### UserProfile
```
id                — UUID
name              — Your name
email             — Your email
interests         — Topics you care about
background        — Your professional background
is_active         — Whether to receive digests
```

---

## 🔧 Configuration

Edit `config.py` to customise:

```python
# Add/remove YouTube channels
YOUTUBE_CHANNEL_IDS = {
    "Channel Name": "UCxxxxxxxxxxxxxxxxxxxxxxx",
}

# Add/remove blog RSS feeds
BLOG_SOURCES = {
    "Blog Name": "https://blog.com/rss.xml",
}

# Control digest size
MAX_VIDEOS_PER_DIGEST   = 5
MAX_ARTICLES_PER_DIGEST = 5
```

---

## ⏰ Scheduling (Daily Automation)

### Windows Task Scheduler

1. Open **Task Scheduler**
2. Create Basic Task → name it "AI New Aggregrator"
3. Trigger: **Daily** at 8:00 AM
4. Action: **Start a Program**
5. Program: `C:\path\to\.venv\Scripts\python.exe`
6. Arguments: `main.py`
7. Start in: `C:\path\to\app\`

### Linux/Mac Cron

```bash
# Run every day at 8:00 AM
0 8 * * * cd /path/to/app && /path/to/.venv/bin/python main.py
```

---

## 🐛 Common Issues & Fixes

### YouTube transcripts being blocked
```
Error: YouTube is blocking requests from your IP
Fix:   Sign up at webshare.io for residential proxies
       Add PROXY_USERNAME and PROXY_PASSWORD to .env
```

### OpenRouter rate limit (429 error)
```
Error: Rate limit exceeded: free-models-per-day
Fix:   Reduce blog sources to 3 and articles per source to 1
       Or add $5 credits at openrouter.ai/settings/credits
```

### Email not sending
```
Error: SMTP authentication failed
Fix:   Use Gmail App Password (not your real password)
       Enable 2-Step Verification first
```

### Database connection error
```
Error: could not translate host name
Fix:   Special characters in password need URL encoding
       Check database/connection.py uses urllib.parse.quote_plus()
```

### DELETE 0 in pgAdmin
```
Meaning: Tables are already empty — not an error!
Fix:     Just run python main.py to populate fresh data
```

---

## 🛠️ Utility Scripts

```bash
# Check what's in your database
python check_db.py

# Clear all data for a fresh start
python clear_db.py

# Re-create your user profile
python seed_user.py
```

---

## 📈 Roadmap

- [ ] Web dashboard to view digest history
- [ ] Telegram bot delivery option
- [ ] Custom relevance scoring per topic
- [ ] Support for more content sources (Reddit, arXiv, Twitter/X)
- [ ] Docker Compose setup for easy deployment
- [ ] Render.com / Railway deployment guide
- [ ] Multiple user profiles support
- [ ] Weekly digest option

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use this for personal or commercial projects.

---

## 🙏 Acknowledgements

- [OpenRouter](https://openrouter.ai) — LLM API access
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) — Transcript fetching
- [Webshare](https://webshare.io) — Proxy services
- [feedparser](https://feedparser.readthedocs.io) — RSS parsing
- [SQLAlchemy](https://sqlalchemy.org) — Database ORM

---

Built with ❤️ to stay on top of the AI world — automatically.
