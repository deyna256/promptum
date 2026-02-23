from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from promptum.providers.exceptions import (
    ProviderHTTPStatusError,
    ProviderNotInitializedError,
    ProviderResponseParseError,
    ProviderRetryExhaustedError,
    ProviderTransientError,
)
from promptum.providers.openrouter import OpenRouterClient
from promptum.providers.retry import RetryConfig, RetryStrategy


def _make_response(
    status_code: int = 200,
    json_data: dict[str, Any] | None = None,
) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json_data,
        request=httpx.Request("POST", "https://fake/chat/completions"),
    )


async def test_generate_without_context_manager_raises_not_initialized():
    client = OpenRouterClient(api_key="test-key")

    with pytest.raises(ProviderNotInitializedError):
        await client.generate(prompt="hello", model="test-model")


async def test_context_manager_closes_client_on_exit():
    client = OpenRouterClient(api_key="test-key")

    async with client:
        inner_client = client._client

    assert inner_client is not None
    assert inner_client.is_closed


async def test_generate_success_returns_content_and_metrics(
    successful_api_response: dict[str, Any],
    no_retry_config: RetryConfig,
):
    async with OpenRouterClient(
        api_key="k",
        default_retry_config=no_retry_config,
    ) as client:
        assert client._client is not None

        mock_post = AsyncMock(
            return_value=_make_response(200, successful_api_response)
        )

        with patch.object(client._client, "post", new=mock_post):
            content, metrics = await client.generate(
                prompt="hello",
                model="test-model",
            )

    assert content == "Hello, world!"
    assert metrics.latency_ms > 0
    assert metrics.prompt_tokens == 10
    assert metrics.completion_tokens == 20
    assert metrics.total_tokens == 30
    assert len(metrics.retry_delays) == 0


async def test_generate_with_system_prompt_includes_system_message(
    successful_api_response: dict[str, Any],
    no_retry_config: RetryConfig,
):
    async with OpenRouterClient(
        api_key="k",
        default_retry_config=no_retry_config,
    ) as client:
        assert client._client is not None

        mock_post = AsyncMock(
            return_value=_make_response(200, successful_api_response)
        )

        with patch.object(client._client, "post", new=mock_post):
            await client.generate(
                prompt="hello",
                model="m",
                system_prompt="Be helpful",
            )

        payload = mock_post.call_args[1]["json"]

    assert payload["messages"][0] == {
        "role": "system",
        "content": "Be helpful",
    }
    assert payload["messages"][1] == {
        "role": "user",
        "content": "hello",
    }


async def test_generate_invalid_response_raises_parse_error(
    no_retry_config: RetryConfig,
):
    async with OpenRouterClient(
        api_key="k",
        default_retry_config=no_retry_config,
    ) as client:
        assert client._client is not None

        mock_post = AsyncMock(return_value=_make_response(200, {"bad": "data"}))

        with patch.object(client._client, "post", new=mock_post), \
            pytest.raises(ProviderResponseParseError):
            await client.generate(prompt="hello", model="m")

async def test_generate_non_retryable_status_raises_http_status_error(
    no_retry_config: RetryConfig,
):
    async with OpenRouterClient(
        api_key="k",
        default_retry_config=no_retry_config,
    ) as client:
        assert client._client is not None

        mock_post = AsyncMock(return_value=_make_response(403))

        with patch.object(client._client, "post", new=mock_post), \
            pytest.raises(ProviderHTTPStatusError):
            await client.generate(prompt="hello", model="m")

@pytest.mark.parametrize("status_code", [429, 500])
async def test_generate_retries_on_retryable_status_then_succeeds(
    successful_api_response: dict[str, Any],
    retry_config_3_attempts: RetryConfig,
    status_code: int,
):
    responses = [
        _make_response(status_code),
        _make_response(200, successful_api_response),
    ]

    async with OpenRouterClient(
        api_key="k",
        default_retry_config=retry_config_3_attempts,
    ) as client:
        assert client._client is not None

        with patch.object(
            client._client,
            "post",
            new=AsyncMock(side_effect=responses),
        ), patch.object(
            client,
            "_sleep",
            new=AsyncMock(),
        ):
            content, _ = await client.generate(prompt="hello", model="m")

    assert content == "Hello, world!"


async def test_generate_exhausts_retries_raises_retry_exhausted(
    retry_config_3_attempts: RetryConfig,
):
    responses = [_make_response(500) for _ in range(3)]

    async with OpenRouterClient(
        api_key="k",
        default_retry_config=retry_config_3_attempts,
    ) as client:
        assert client._client is not None

        with patch.object(
            client._client,
            "post",
            new=AsyncMock(side_effect=responses),
        ), patch.object(
            client,
            "_sleep",
            new=AsyncMock(),
        ), pytest.raises(ProviderRetryExhaustedError) as exc_info:
            await client.generate(prompt="hello", model="m")

    err = exc_info.value
    assert err.attempts == 3
    assert err.last_status_code == 500
    assert isinstance(err.last_response_body, str)
    assert len(err.retry_delays) == 2


async def test_generate_retry_delays_recorded_in_metrics(
    successful_api_response: dict[str, Any],
    retry_config_3_attempts: RetryConfig,
):
    responses = [
        _make_response(429),
        _make_response(429),
        _make_response(200, successful_api_response),
    ]

    async with OpenRouterClient(
        api_key="k",
        default_retry_config=retry_config_3_attempts,
    ) as client:
        assert client._client is not None

        with patch.object(
            client._client,
            "post",
            new=AsyncMock(side_effect=responses),
        ), patch.object(
            client,
            "_sleep",
            new=AsyncMock(),
        ):
            _, metrics = await client.generate(prompt="hello", model="m")

    assert len(metrics.retry_delays) == 2
    assert all(d > 0 for d in metrics.retry_delays)


async def test_generate_transient_error_exhausts_retries_raises_transient_error(
    retry_config_3_attempts: RetryConfig,
):
    async with OpenRouterClient(
        api_key="k",
        default_retry_config=retry_config_3_attempts,
    ) as client:
        assert client._client is not None

        with patch.object(
            client._client,
            "post",
            new=AsyncMock(side_effect=httpx.ReadTimeout("timed out")),
        ), patch.object(
            client,
            "_sleep",
            new=AsyncMock(),
        ), pytest.raises(ProviderTransientError) as exc_info:
            await client.generate(prompt="hello", model="m")

    err = exc_info.value
    assert err.attempts == 3
    assert len(err.retry_delays) == 2


def test_calculate_delay_exponential_backoff():
    client = OpenRouterClient(api_key="k")
    config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        initial_delay=1.0,
        exponential_base=2.0,
        max_delay=60.0,
    )

    assert client._calculate_delay(0, config) == 1.0
    assert client._calculate_delay(1, config) == 2.0
    assert client._calculate_delay(2, config) == 4.0
    assert client._calculate_delay(3, config) == 8.0


def test_calculate_delay_exponential_capped_at_max():
    client = OpenRouterClient(api_key="k")
    config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        initial_delay=1.0,
        exponential_base=2.0,
        max_delay=5.0,
    )

    assert client._calculate_delay(0, config) == 1.0
    assert client._calculate_delay(3, config) == 5.0
    assert client._calculate_delay(10, config) == 5.0


def test_calculate_delay_fixed_returns_initial():
    client = OpenRouterClient(api_key="k")
    config = RetryConfig(
        strategy=RetryStrategy.FIXED_DELAY,
        initial_delay=2.5,
    )

    assert client._calculate_delay(0, config) == 2.5
    assert client._calculate_delay(1, config) == 2.5
    assert client._calculate_delay(5, config) == 2.5


async def test_generate_uses_per_call_retry_config_over_default(
    successful_api_response: dict[str, Any],
):
    default_config = RetryConfig(max_attempts=1)
    per_call_config = RetryConfig(
        max_attempts=3,
        initial_delay=0.01,
        max_delay=0.1,
    )

    responses = [
        _make_response(500),
        _make_response(200, successful_api_response),
    ]

    async with OpenRouterClient(
        api_key="k",
        default_retry_config=default_config,
    ) as client:
        assert client._client is not None

        with patch.object(
            client._client,
            "post",
            new=AsyncMock(side_effect=responses),
        ), patch.object(
            client,
            "_sleep",
            new=AsyncMock(),
        ):
            content, _ = await client.generate(
                prompt="hello",
                model="m",
                retry_config=per_call_config,
            )

    assert content == "Hello, world!"
