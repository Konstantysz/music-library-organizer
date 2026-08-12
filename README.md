# Music Library Organizer

A Python tool that standardizes FLAC music library folder structures and filenames using audio metadata tags.

## What It Does

- Renames album directories to `Artist - Album (Year)`.
- Combines primary artists and album artists, placing album artists first.
- Renames FLAC files to `01 Track Title.flac` (or `1-01 Track Title.flac` for multi-disc releases).
- Handles mixed track tag formats like `1.01`, `1-01`, and `01/12`.
- Cleans invalid Windows path characters (`:`, `*`, `?`, `"`, `<`, `>`, `|`) and handles case-only directory renames safely.

## Installation

This project uses `uv` for dependency management.

```bash
uv sync
```

## Usage

### Preview changes (Dry Run)

Run `--dry-run` to preview how files and directories will be renamed without making changes on disk:

```bash
uv run music-library-organizer /path/to/music/library --dry-run
```

### Apply changes

To rename directories and files in place:

```bash
uv run music-library-organizer /path/to/music/library
```

If no directory path is provided, it scans the current working directory.

## Running Tests

Run the test suite with `pytest`:

```bash
uv run pytest
```

Check code style and linting:

```bash
uv run ruff check .
```
