


import sys
from database.connection import init_db
from scrapers.blog_scraper import BlogScraper
from agents.digest_agent import DigestAgent
from agents.curator_agent import CuratorAgent
from agents.email_agent import EmailAgent


def run_pipeline(send_email: bool = True):
    print("=" * 60)
    print("🚀  AI News Aggregator – Starting Pipeline")
    print("=" * 60)

    # Step 0 – Init DB
    print("\n📦 Step 0: Initialising database...")
    init_db()

    # Step 1 – Blogs only
    print("\n📰 Step 1: Scraping blog RSS feeds...")
    BlogScraper().run()

    # Step 2 – Summarise
    print("\n🤖 Step 2: DigestAgent – generating AI summaries...")
    DigestAgent().run()

    # Step 3 – Rank
    print("\n🎯 Step 3: CuratorAgent – ranking by relevance...")
    top_items = CuratorAgent().run()

    # Step 4 – Email
    if send_email:
        print("\n📧 Step 4: EmailAgent – sending digest...")
        ok = EmailAgent().run(top_items)
        status = "✅ Digest sent!" if ok else "⚠️  Email failed – check SMTP settings."
    else:
        print("\n⏭  Step 4: Email skipped (--no-email).")
        status = "✅ Done – pipeline complete."

    print(f"\n{status}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline(send_email="--no-email" not in sys.argv)