from abc import ABC, abstractmethod
from typing import Any

from promptum.providers.metrics import Metrics
from promptum.providers.retry import RetryConfig


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        temperature: float = 1.0,
        max_tokens: int | None = None,
        retry_config: RetryConfig | None = None,
        **kwargs: Any,
    ) -> tuple[str, Metrics]:
        """
        Generates a response from the LLM.

        Returns:
            (response_text, metrics)
        """
