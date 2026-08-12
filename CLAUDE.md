# Agent Guidelines for Music Library Organizer

Guidelines for AI agents working in this repository.

## Environment & Tooling

- Package manager: `uv`
- Python version: `>=3.12`
- Main dependencies: `tinytag`
- Dev dependencies: `pytest`, `ruff`

## Development Rules

### Filesystem & Safety
- **Dry-run First**: Always ensure file mutation code supports `--dry-run` to preview actions before modifying disk state.
- **Windows Case Safety**: Use `safe_rename()` when renaming files or folders to handle case-only changes (e.g. `album -> Album`) on Windows NTFS.
- **No Hardcoded Paths**: Accept library paths via CLI parameters or environment variables rather than hardcoding local drive letters.

### Metadata & Naming Conventions
- Album directory pattern: `Artist - Album (Year)`.
- Track filename pattern: `01 Title.flac` for single-disc releases, `1-01 Title.flac` for multi-disc releases.
- Sanitize invalid path characters (`:`, `*`, `?`, `"`, `<`, `>`, `|`) and reserved Windows keywords (`CON`, `PRN`, `AUX`, `NUL`).
- Default unknown metadata to clean placeholders (`0000`, `Unknown Artist`, `Unknown Album`).

### Code Quality & Testing
- Keep core metadata logic modular and pure so helper functions can be unit tested without requiring real FLAC audio files.
- Run `uv run pytest` to verify unit tests pass.
- Run `uv run ruff check .` to check formatting and linting.
