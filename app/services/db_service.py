# app/services/db_service.py

from app.db import get_connection

def save_video(video: dict):
    """
    Saves a video to the 'videos' table in PostgreSQL.
    Uses ON CONFLICT to avoid duplicate entries.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO videos (
                video_id,
                channel_id,
                title,
                url,
                published_at,
                transcript,
                transcript_status,
                summary,
                relevance_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO NOTHING;
        """, (
            video["video_id"],
            video["channel_id"],
            video["title"],
            video["link"],
            video["published_at"],
            video.get("transcript_text"),
            video.get("transcript_status"),
            video.get("summary"),
            video.get("relevance_score")
        ))

        conn.commit()

    except Exception as e:
        print("Database Error:", e)
        conn.rollback()

    finally:
        cur.close()
        conn.close()


def save_digest(article_id: str, article_type: str, title: str, summary: str):
    """
    Saves AI-generated summaries into the 'digest' table.
    Uses ON CONFLICT to prevent duplicate summaries for the same article.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO digest (article_id, article_type, title, summary)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (article_id) DO NOTHING;
        """, (
            article_id,
            article_type,
            title,
            summary
        ))

        conn.commit()

    except Exception as e:
        print("Digest Database Error:", e)
        conn.rollback()

    finally:
        cur.close()
        conn.close()