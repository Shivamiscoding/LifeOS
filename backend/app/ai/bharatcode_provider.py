"""BharatCode AI provider — real HTTP implementation."""
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.ai.provider import AIProvider
from app.config import get_settings
from app.schemas.ai_schemas import AIResponse

logger = logging.getLogger(__name__)
settings = get_settings()


class BharatCodeProvider(AIProvider):
    """Calls the BharatCode chat completions API."""

    @property
    def provider_name(self) -> str:
        return "BharatCode"

    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        payload: Dict[str, Any] = {
            "model": "bharatcode-v1",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        headers = {
            "Authorization": f"Bearer {settings.bharatcode_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.bharatcode_api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            choice = data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content") or ""

            return AIResponse(
                content=content,
                raw_response=data,
            )

        except httpx.HTTPStatusError as exc:
            logger.error("BharatCode API HTTP error %s: %s", exc.response.status_code, exc.response.text)
            raise RuntimeError(f"BharatCode API error: {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            logger.error("BharatCode API request error: %s", exc)
            raise RuntimeError(f"BharatCode API connection error: {exc}") from exc
        except Exception as exc:
            logger.error("BharatCode API unexpected error: %s", exc)
            raise RuntimeError(f"BharatCode API unexpected error: {exc}") from exc
