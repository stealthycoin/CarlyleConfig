sync:
    uv sync


test: sync
    uv run pytest


check: sync
    uv run ruff check src/ test/
    uv run ruff format --check src/ test/
    uv run mypy --strict --show-error-codes src/


format:
    uv run ruff format


prcheck: check test


bump:
    uv run bumpver update --no-fetch --patch --no-push --commit --tag-commit


bump-dry:
    uv run bumpver update --no-fetch --patch --no-push --commit --tag-commit --dry


build:
    uv build


publish:
    uvx twine upload dist/*


clean:
    rm -rf dist
