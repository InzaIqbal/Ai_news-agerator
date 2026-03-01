"""
agents/base_agent.py
"""

import os
from abc import ABC, abstractmethod
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class BaseAgent(ABC):
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        )
        self.model = os.getenv("OPENAI_MODEL", "openai/o1")

    @abstractmethod
    def run(self, *args, **kwargs):
        ...

    def chat(self, system: str, user: str, **kwargs) -> str:
        """
        Single-turn LLM call.
        **kwargs absorbs any extra arguments like max_tokens
        so old code doesn't break.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return response.choices[0].message.content.strip()