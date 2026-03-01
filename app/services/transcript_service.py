from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

def get_video_transcript(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()

        # Try English first, then fallback languages
        transcript = ytt_api.fetch(video_id, languages=["en"])

        full_text = " ".join(snippet.text for snippet in transcript)

        return {
            "status": "available",
            "text": full_text
        }

    except (TranscriptsDisabled, NoTranscriptFound):
        return {
            "status": "not_available",
            "text": None
        }

    except VideoUnavailable:
        return {
            "status": "video_unavailable",
            "text": None
        }

    except Exception as e:
        return {
            "status": f"error: {str(e)}",
            "text": None
        }