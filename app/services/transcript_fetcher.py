"""
services/transcript_fetcher.py

Fetches YouTube transcripts using yt-dlp — completely FREE, no proxy needed.

Strategy:
  1. Try yt-dlp with manual English captions
  2. Try yt-dlp with auto-generated English captions
  3. Fallback to youtube-transcript-api (old method)
  4. Return None if all fail

HOW TO SET UP (one-time):
  pip install yt-dlp

OPTIONAL — use your browser cookies to avoid bot detection:
  See README section "Cookie Setup" below.
"""

import os
import re
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────
# COOKIE SETUP (optional but recommended)
# ─────────────────────────────────────────────────────────────────
#
# If YouTube starts blocking yt-dlp, export your browser cookies:
#
# Step 1: Install the browser extension:
#   Chrome: "Get cookies.txt LOCALLY"
#   Firefox: "cookies.txt"
#
# Step 2: Go to youtube.com while logged in → export cookies.txt
#
# Step 3: Put the file at:  app/cookies/youtube.txt
#
# That's it. The code below picks it up automatically.
# ─────────────────────────────────────────────────────────────────

COOKIES_PATH = Path(__file__).parent.parent / "cookies" / "youtube.txt"


def _get_ydl_base_opts() -> dict:
    """Base yt-dlp options shared across all calls."""
    opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": False,
    }
    # Auto-load cookies if the file exists
    if COOKIES_PATH.exists():
        opts["cookiefile"] = str(COOKIES_PATH)
        print(f"   🍪 Using cookies from {COOKIES_PATH}")
    return opts


def _parse_vtt(vtt_text: str) -> str:
    """
    Convert a VTT subtitle string into clean plain text.

    VTT files look like:
        WEBVTT
        00:00:01.000 --> 00:00:04.000
        Hello this is <c>spoken</c> text

    We strip all the timestamps and HTML tags, deduplicate
    repeated lines (VTT auto-captions repeat a lot), and
    join everything into one clean paragraph.
    """
    lines = vtt_text.strip().split("\n")
    text_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip VTT header lines
        if line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue
        # Skip timestamp lines like "00:00:01.000 --> 00:00:04.000"
        if re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        # Remove inline HTML tags: <c>, </c>, <00:00:01.000>, etc.
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line:
            text_lines.append(line)

    # Deduplicate consecutive identical lines
    # (auto-captions often repeat the same line across multiple cues)
    deduped = []
    prev = None
    for line in text_lines:
        if line != prev:
            deduped.append(line)
        prev = line

    return " ".join(deduped)


def _fetch_via_ytdlp(video_id: str, use_auto: bool = False) -> Optional[str]:
    """
    Download subtitles for a video using yt-dlp.

    Args:
        video_id:  YouTube video ID (e.g. "dQw4w9WgXcQ")
        use_auto:  If True, fetch auto-generated captions.
                   If False, fetch manually uploaded captions.

    Returns:
        Clean transcript text, or None if unavailable.
    """
    try:
        import yt_dlp
    except ImportError:
        print("   ❌ yt-dlp not installed. Run: pip install yt-dlp")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        opts = _get_ydl_base_opts()
        opts.update({
            "outtmpl": os.path.join(tmpdir, "%(id)s"),
            "subtitleslangs": ["en", "en-US", "en-GB"],
            "subtitlesformat": "vtt",
        })

        if use_auto:
            opts["writeautomaticsub"] = True
            opts["writesubtitles"] = False
        else:
            opts["writesubtitles"] = True
            opts["writeautomaticsub"] = False

        url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as e:
            # yt-dlp raises even on "no subtitles" — that's expected
            err = str(e)
            if "no subtitles" in err.lower() or "requested format" in err.lower():
                return None
            # Real errors (network, bot detection, etc.)
            print(f"   ⚠️  yt-dlp error ({'auto' if use_auto else 'manual'}): {err[:120]}")
            return None

        # Find the downloaded .vtt file
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            return None

        vtt_text = vtt_files[0].read_text(encoding="utf-8", errors="replace")
        transcript = _parse_vtt(vtt_text)

        if len(transcript.strip()) < 50:
            return None  # Too short to be useful

        return transcript


def _fetch_via_transcript_api(video_id: str) -> Optional[str]:
    """
    Fallback: use youtube-transcript-api (the old method).
    May get blocked without a proxy, but worth trying.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
        )

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=["en", "en-US"])
        text = " ".join(snippet.text for snippet in transcript.snippets)
        return text if len(text) > 50 else None

    except Exception as e:
        print(f"   ⚠️  transcript-api fallback failed: {str(e)[:80]}")
        return None


def get_transcript(video_id: str) -> dict:
    """
    Main entry point. Tries multiple strategies in order.

    Returns a dict:
        {
            "status": "available" | "unavailable",
            "text":   "full transcript..." | None,
            "method": "yt-dlp-manual" | "yt-dlp-auto" | "api" | None,
            "error":  None | "reason string"
        }
    """
    print(f"   🎬 Fetching transcript for video: {video_id}")

    # ── Strategy 1: yt-dlp manual captions ──────────────────────
    print("   📝 Trying yt-dlp (manual captions)...")
    text = _fetch_via_ytdlp(video_id, use_auto=False)
    if text:
        print(f"   ✅ Got transcript via yt-dlp manual ({len(text)} chars)")
        return {"status": "available", "text": text[:8000], "method": "yt-dlp-manual", "error": None}

    # ── Strategy 2: yt-dlp auto-generated captions ───────────────
    print("   📝 Trying yt-dlp (auto-generated captions)...")
    text = _fetch_via_ytdlp(video_id, use_auto=True)
    if text:
        print(f"   ✅ Got transcript via yt-dlp auto ({len(text)} chars)")
        return {"status": "available", "text": text[:8000], "method": "yt-dlp-auto", "error": None}

    # ── Strategy 3: youtube-transcript-api fallback ───────────────
    print("   📝 Trying youtube-transcript-api (fallback)...")
    text = _fetch_via_transcript_api(video_id)
    if text:
        print(f"   ✅ Got transcript via transcript-api ({len(text)} chars)")
        return {"status": "available", "text": text[:8000], "method": "api", "error": None}

    # ── All strategies failed ─────────────────────────────────────
    print(f"   ❌ No transcript available for {video_id}")
    return {
        "status": "unavailable",
        "text": None,
        "method": None,
        "error": "All strategies failed — no captions found",
    }