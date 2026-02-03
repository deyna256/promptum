from typing import Any, Protocol


class Validator(Protocol):
    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        """
        Validates a response string.

        Returns:
            (passed, details) where details contains diagnostic information
        """
        ...

    def describe(self) -> str:
        """Returns a human-readable description of validation criteria."""
        ...
