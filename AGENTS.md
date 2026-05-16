# Agent Guidance for python-aes

## Project
Pure Python AES256 implementation (CBC and CTR modes). Educational project with practical use.

## Key Commands
- `poetry install` - Install dependencies
- `poetry run pytest` - Run all tests
- `poetry run pytest tests/unit/` - Run unit tests only
- `poetry run pre-commit run -a` - Run all pre-commit hooks
- `poetry run ruff check .` - Lint only

## Dependencies
- Runtime: aiofiles
- Test: pytest, pytest-asyncio, pytest-cov
- Lint: ruff, pre-commit, mypy, bandit

## CI
- GitHub Actions: Python 3.12, runs pre-commit then pytest with coverage

## Workflow Rules

**Formatting**
- Only at end of tasks, not during implementation

**Linting**
- OK during tasks

**Testing**
- Tests must pass at end of each task
- Test implementation can run in parallel subagents
- TDD not strictly required
- After test failure: report reason (assertion failure vs exception)
- Max 10 retries on failing tests, then ask whether to continue
