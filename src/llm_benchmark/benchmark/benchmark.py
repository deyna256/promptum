import asyncio
from collections.abc import Callable, Sequence
from typing import Any

from llm_benchmark.benchmark.report import Report
from llm_benchmark.core.result import TestResult
from llm_benchmark.core.test_case import TestCase
from llm_benchmark.execution.runner import Runner
from llm_benchmark.providers.protocol import LLMProvider


class Benchmark:
    def __init__(
        self,
        provider: LLMProvider,
        name: str = "benchmark",
        max_concurrent: int = 5,
        progress_callback: Callable[[int, int, TestResult], None] | None = None,
    ):
        self.provider = provider
        self.name = name
        self.max_concurrent = max_concurrent
        self.progress_callback = progress_callback
        self._test_cases: list[TestCase] = []

    def add_test(self, test_case: TestCase) -> None:
        self._test_cases.append(test_case)

    def add_tests(self, test_cases: Sequence[TestCase]) -> None:
        self._test_cases.extend(test_cases)

    def run(self, metadata: dict[str, Any] | None = None) -> Report:
        return asyncio.run(self.run_async(metadata))

    async def run_async(self, metadata: dict[str, Any] | None = None) -> Report:
        if not self._test_cases:
            return Report(results=[], metadata=metadata or {})

        runner = Runner(
            provider=self.provider,
            max_concurrent=self.max_concurrent,
            progress_callback=self.progress_callback,
        )

        results = await runner.run(self._test_cases)

        return Report(
            results=results,
            metadata=metadata or {},
        )
