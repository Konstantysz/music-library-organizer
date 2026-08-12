# Agent Guidelines for Music Library Organizer

Guidelines for AI agents working in this repository.

## Environment & Tooling

- Package manager: `uv`
- Python version: `>=3.12`
- Main dependencies: `tinytag`
- Dev dependencies: `pytest`, `ruff`, `pre-commit`

## Development Rules

### Filesystem & Safety
- **Dry‑run First**: All mutating actions support `--dry-run`.
- **Windows Case Safety**: Use `safe_rename()` for case‑only renames.
- **No Hard‑coded Paths**: Accept paths via CLI or environment variables.

### Metadata & Naming
- Album format: `Artist - Album (Year)`.
- Track format: `01 Title.flac` (single‑disc) or `1-01 Title.flac` (multi‑disc).
- Sanitize invalid characters (`: * ? " < > |`) and reserved Windows names.
- Fallback placeholders: `0000`, `Unknown Artist`, `Unknown Album`.

### Code Quality & Testing
- Keep core logic pure and modular.
- Run `uv run pytest` to verify tests.
- Run `uv run ruff check .` for linting.
- Run `uv run pre-commit run --all-files` for formatting.

## Formatting Rules (Ruff)

See `pyproject.toml` for the full configuration:
- Line length: 100
- Target Python: 3.12
- Quote style: double
- Indent style: space
- No magic trailing commas
- Auto line endings
- Lint selections: `E, F, I, N, UP, B, SIM, C4, PTH, DOC` (ignore `D100`)

## Pre‑commit Hooks

Setup:
```bash
uv run pre-commit install
```
Run on all files:
```bash
uv run pre-commit run --all-files
```
Included hooks:
- `ruff-format`
- `ruff-check` (with `--fix`)
- End‑of‑file fixer
- Trailing whitespace remover
- YAML and TOML checkers

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes and pull requests:
- Installs `uv` and project dependencies.
- Executes Ruff format check, Ruff lint check, and test suite.
- Enforces code style automatically.

## Commit Style
- Summary < 60 chars, start with a capital word.
- Write like a casual text message; drop unnecessary words.
- No bullet points, Markdown, or backticks in the body.
- Avoid AI clichés (`leverage`, `utilize`, `streamline`, …).
- Emojis are fine if you’d actually use them.
- No formal footers; weave any credit into the description.

### Good Commit Examples
- `Fix login redirect loop, thx copilot for the state check`
- `Make button bigger, users keep missing it`
- `Add basic rate limiter, ai did most of it, i cleaned up tests`
- `Oops, forgot to update the env example`
- `Tweak timeout, prod was crying`

### Bad Commit Examples
- `This commit refactors the authentication middleware to leverage a more robust error‑handling paradigm.`
- `* feat: implement pagination`
- `Addressed an issue where the logout endpoint was not correctly invalidating the session token.`
- `Co‑developed with AI to streamline the database query logic.`
