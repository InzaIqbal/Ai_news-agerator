# app/services/ai_service.py

import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

# Load OpenRouter API key from .env
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI/OpenRouter client
client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def generate_summary_and_relevance(transcript_text: str, user_profile: str):
    """
    Generates a 2-3 sentence summary and a relevance score (1-10)
    for a given transcript, tailored to the user's profile.
    """
    if not transcript_text:
        return {"summary": None, "relevance_score": 0}

    prompt = f"""
Transcript:
{transcript_text}

Task:
1. Provide a concise 2-3 sentence summary of the above video.
2. Rate the relevance from 1 to 10 based on this user profile: {user_profile}

Respond ONLY in valid JSON:
{{
    "summary": "...",
    "relevance_score": 7
}}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b:free",   # 🔥 Replace with your preferred model
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()

        # Safe JSON parsing
        data = json.loads(content)

        return {
            "summary": data.get("summary"),
            "relevance_score": data.get("relevance_score")
        }

    except Exception as e:
        print("OpenRouter Error:", e)
        return {"summary": None, "relevance_score": 0}