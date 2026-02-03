from typing import Protocol

from llm_benchmark.core.result import TestResult
from llm_benchmark.core.test_case import TestCase


class BenchmarkHook(Protocol):
    def before_test(self, test_case: TestCase) -> None:
        """Called before each test execution."""
        ...

    def after_test(self, result: TestResult) -> None:
        """Called after each test execution."""
        ...
