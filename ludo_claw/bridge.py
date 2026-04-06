import httpx
import os
from typing import Dict, Any, List

class OpenRouterBridge:
    """
    Clean, httpx-based bridge for communicating with OpenRouter.
    Replaces the old axios/telemetry-heavy implementation.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ludo-claw", # Optional, for OpenRouter rankings
            "X-Title": "Ludo-Claw Framework" # Optional, for OpenRouter rankings
        }

    async def generate_response(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Calls the OpenRouter API to generate a chat completion.
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not set.")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def generate_response_sync(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Synchronous wrapper for generating a response.
        """
        import asyncio
        return asyncio.run(self.generate_response(model, messages, temperature))
