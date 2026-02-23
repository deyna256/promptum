import json
import re
from typing import Any

from promptum.validation.validator import Validator


class ExactMatch(Validator):
    __slots__ = ("expected", "case_sensitive")

    def __init__(self, expected: str, case_sensitive: bool = True) -> None:
        self.expected = expected
        self.case_sensitive = case_sensitive

    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        if self.case_sensitive:
            passed = response == self.expected
        else:
            passed = response.lower() == self.expected.lower()

        return passed, {
            "expected": self.expected,
            "actual": response,
            "case_sensitive": self.case_sensitive,
        }

    def describe(self) -> str:
        mode = "case-sensitive" if self.case_sensitive else "case-insensitive"
        return f"Exact match ({mode}): {self.expected!r}"


class Contains(Validator):
    __slots__ = ("substring", "case_sensitive")

    def __init__(self, substring: str, case_sensitive: bool = True) -> None:
        self.substring = substring
        self.case_sensitive = case_sensitive

    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        if self.case_sensitive:
            passed = self.substring in response
        else:
            passed = self.substring.lower() in response.lower()

        return passed, {
            "substring": self.substring,
            "case_sensitive": self.case_sensitive,
        }

    def describe(self) -> str:
        mode = "case-sensitive" if self.case_sensitive else "case-insensitive"
        return f"Contains ({mode}): {self.substring!r}"


class Regex(Validator):
    __slots__ = ("pattern", "flags")

    def __init__(self, pattern: str, flags: int = 0) -> None:
        self.pattern = pattern
        self.flags = flags

    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        match = re.search(self.pattern, response, self.flags)
        return match is not None, {
            "pattern": self.pattern,
            "matched": match.group(0) if match else None,
        }

    def describe(self) -> str:
        return f"Regex: {self.pattern!r}"


class JsonSchema(Validator):
    __slots__ = ("required_keys",)

    def __init__(self, required_keys: tuple[str, ...] = ()) -> None:
        self.required_keys = required_keys

    def validate(self, response: str) -> tuple[bool, dict[str, Any]]:
        try:
            data = json.loads(response)
            if not isinstance(data, dict):
                return False, {"error": "Response is not a JSON object"}

            missing_keys = [key for key in self.required_keys if key not in data]
            passed = len(missing_keys) == 0

            return passed, {
                "parsed": data,
                "missing_keys": missing_keys,
            }
        except json.JSONDecodeError as e:
            return False, {"error": f"Invalid JSON: {e}"}

    def describe(self) -> str:
        if self.required_keys:
            keys = ", ".join(self.required_keys)
            return f"Valid JSON with keys: {keys}"
        return "Valid JSON object"
