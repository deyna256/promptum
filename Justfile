# Sync dependencies from pyproject.toml
sync:
    uv sync

# Run type checking with ty
type:
    uv run ty check src/promptum

# Run ruff linter with automatic fixes
style:
    uv run ruff check src/promptum tests

# Format code
format:
    uv run ruff format src/promptum tests

# Run all tests with pytest (coverage enabled by default)
test:
    uv run pytest tests/ -v

# Generate and open HTML coverage report
[unix]
cov:
    uv run pytest tests/ --cov-report=html
    {{ if os() == "linux" { "xdg-open" } else { "open" } }} htmlcov/index.html

[windows]
cov:
    uv run pytest tests/ --cov-report=html
    start htmlcov/index.html

# Clean up generated files and caches
[unix]
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov results/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

[windows]
clean:
    if exist .pytest_cache rmdir /s /q .pytest_cache
    if exist .ruff_cache rmdir /s /q .ruff_cache
    if exist .coverage del .coverage
    if exist htmlcov rmdir /s /q htmlcov
    if exist results rmdir /s /q results
    for /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
    for /r . %%f in (*.pyc) do @del "%%f"
