"""Abstract AI provider interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.schemas.ai_schemas import AIResponse


class AIProvider(ABC):
    """Abstract base class for all AI providers."""

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AIResponse:
        """
        Send messages to the AI and return a structured response.

        Args:
            messages: List of {"role": "user"|"assistant"|"system", "content": str}
            tools: Optional list of tool definitions (OpenAI-compatible)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            AIResponse with content and optional ActionPlan
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of this provider."""
        ...
