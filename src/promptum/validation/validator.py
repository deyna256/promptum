from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    @abstractmethod
    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        """
        Validates a response string.

        Returns:
            (passed, details) where details contains diagnostic information
        """

    @abstractmethod
    def describe(self) -> str:
        """Returns a human-readable description of validation criteria."""
