# Link Classification

Generate structured metadata for a list of URLs. The pipeline reads `links.md`, fetches page content, classifies each link, and writes results to JSON.

## Quickstart

```bash
uv sync
cp .env.example .env
```

Set `OPENROUTER_API_KEY` in `.env`, add URLs to `links.md`, then run:

```bash
uv run main.py
```

Results are written to `data/links.json`.

## Command Reference

- Install deps: `uv sync` (creates a local environment and installs packages)
- Run pipeline: `uv run main.py` (reads `links.md` and writes `data/links.json`)
- Run tests: `uv run pytest` (executes the test suite)

## Architecture

Data flow:

1. `links.md` is parsed by `utils.extract_urls`.
2. `pipeline.process_links` deduplicates URLs and runs concurrent classification.
3. `classifier.Classifier` fetches metadata and calls the LLM.
4. `storage.LinkStore` writes records to `data/links.json`.

Design principles:

- Deterministic input: URL order is preserved after deduplication.
- Idempotent writes: existing URLs are skipped by normalized URL.
- Simple I/O: JSON file storage to keep dependencies minimal.

## Output Format

`data/links.json`:

```json
{
    "links": [
        {
            "id": 1,
            "url": "https://github.com/astral-sh/ruff",
            "normalized_url": "https://github.com/astral-sh/ruff",
            "domain": "github.com",
            "title": "Ruff",
            "description": "Fast Python linter and formatter written in Rust",
            "site_name": "GitHub",
            "image_url": null,
            "category": "code",
            "context": "Useful for Python developers seeking faster linting",
            "created_at": "2026-01-01T00:00:00+00:00"
        }
    ],
    "next_id": 2
}
```

## Project Structure

- `main.py` entry point
- `src/` core modules (`fetcher.py`, `classifier.py`, `pipeline.py`, `storage.py`)
- `tests/` pytest tests
- `data/` output directory
- `links.md` input file
- `.env.example` configuration template

## Configuration

Environment variables (via `.env`):

- `OPENROUTER_API_KEY` required
- `OPENROUTER_MODEL` default `openai/gpt-4o-mini`
- `OPENROUTER_BASE_URL` default `https://openrouter.ai/api/v1`

- `LINKREC_DATA_PATH` default `data/links.json`
- `LINKREC_MAX_CONCURRENCY` default `8`
- `LINKREC_TIMEOUT` default `12` seconds

## Contributing

- Read `AGENTS.md` for repository guidelines.
- Keep changes small and focused; add or update tests in `tests/`.
- Follow PEP 8 style with 4-space indentation and `snake_case` naming.
- Include a short description of what changed and how to run tests.

## Minimal Example

`links.md`:

```markdown
https://github.com/astral-sh/ruff
```

Run `uv run main.py` to generate `data/links.json`.
