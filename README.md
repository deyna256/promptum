# promptum

<div align="center">

![Python 3.13+](https://img.shields.io/badge/Python-3.13+-blue?style=for-the-badge&logo=python)
![Async](https://img.shields.io/badge/Async-First-green?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
[![PyPI Version](https://img.shields.io/pypi/v/promptum?style=for-the-badge&logo=pypi&logoColor=white&color=orange)](https://pypi.org/project/promptum/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/promptum?style=for-the-badge&logo=pypi&logoColor=white&color=blueviolet)](https://pypi.org/project/promptum/)

**Test LLMs Like a Pro.**

Stop writing boilerplate to test LLMs. Start getting results.

</div>

---

## What's This?

You're choosing between GPT-4, Claude, and Gemini for your product. You need to know which one actually handles *your* prompts better — not some generic benchmark, but your real tasks, your edge cases, your expected formats.

**promptum** turns that into a few lines of Python. One client for 100+ models, automatic retries, latency/cost/token tracking, structured validation — all async, all typed, zero config files.

```python
session = Session(provider=client, name="my_test")
session.add_test(Prompt(
    name="basic_math",
    prompt="What is 2+2?",
    model="openai/gpt-3.5-turbo",
    validator=Contains("4"),
))
report = await session.run()
summary = report.get_summary()
```

No YAML. No config files. Just Python you can read in 30 seconds.

---

## Quick Start

```bash
pip install promptum  # (or: uv pip install promptum)
export OPENROUTER_API_KEY="your-key"
```

```python
import asyncio
from promptum import Session, Prompt, OpenRouterClient, Contains

async def main():
    async with OpenRouterClient(api_key="your-key") as client:
        session = Session(provider=client, name="quick_test")

        session.add_test(Prompt(
            name="basic_math",
            prompt="What is 15 * 7? Reply with just the number.",
            model="openai/gpt-3.5-turbo",
            validator=Contains("105"),
        ))

        report = await session.run()
        summary = report.get_summary()

        print(f"Passed: {summary.passed}/{summary.total}")
        print(f"Avg latency: {summary.avg_latency_ms:.0f}ms")
        print(f"Total cost: ${summary.total_cost_usd:.6f}")

asyncio.run(main())
```

---

## Why promptum?

Most LLM testing is ad-hoc scripts that grow into unmaintainable messes. You end up with separate API clients per provider, hand-rolled retry logic, manual latency tracking, and validation scattered across files.

promptum replaces all of that with a single coherent API:

- [x] **100+ Models via OpenRouter** — one client for OpenAI, Anthropic, Google, and more
- [x] **Smart Validation** — ExactMatch, Contains, Regex, JsonSchema, or write your own
- [x] **Automatic Retries** — exponential/fixed-delay backoff with configurable attempts
- [x] **Metrics Tracking** — latency, tokens, cost — automatically captured
- [x] **Async by Default** — run tests in parallel with concurrency control
- [x] **Extensible** — implement `LLMProvider` or `Validator` to plug in any model or validation logic
- [x] **Type Safe** — full type hints, catches errors before runtime

---

## Documentation

- [Session & Testing](docs/session.md) — Session, Prompt, Report, Summary, TestResult
- [Providers](docs/providers.md) — LLMProvider, OpenRouterClient, Metrics, Retry, Exceptions
- [Validation](docs/validation.md) — Validator, ExactMatch, Contains, Regex, JsonSchema

---

## Requirements

- Python 3.13+
- An OpenRouter API key (or implement your own provider)

---

## Contributing

Found a bug? Want a feature? PRs welcome!

```bash
git clone https://github.com/deyna256/promptum.git
cd promptum
just sync     # Install dependencies
just test     # Run tests
just style    # Check code style
just format   # Format code
just type     # Type checking
```

---

## License

MIT - do whatever you want with it.

---

<div align="center">

**[Star on GitHub](https://github.com/deyna256/promptum)** | **[Report Bug](https://github.com/deyna256/promptum/issues)** | **[Request Feature](https://github.com/deyna256/promptum/issues)**

Made for developers who value their time.

</div>
