import argparse
import logging
import os
import re
from pathlib import Path

from tinytag import TinyTag


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[94m",
        logging.INFO: "\033[92m",
        logging.WARNING: "\033[93m",
        logging.ERROR: "\033[91m",
        logging.CRITICAL: "\033[91m\033[1m",
    }
    RESET = "\033[0m"

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelno, '')}%(levelname)s: %(message)s{self.RESET}"
        if record.levelno == logging.INFO:
            log_fmt = f"{self.COLORS.get(record.levelno, '')}%(message)s{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def extract_year(val):
    if val is None:
        return "0000"
    s = str(val).strip()
    match = re.search(r"\b(19\d{2}|20\d{2})\b", s)
    if match:
        return match.group(1)
    match = re.search(r"\d{4}", s)
    if match:
        return match.group(0)
    return "0000"


def format_artists(artist_val, albumartist_val):
    if not artist_val and not albumartist_val:
        return "Unknown Artist"

    def split_artists(s) -> list[str]:
        if not s:
            return []
        parts = re.split(r"\s*;\s*|\s*/\s*|\s*\\\\\s*|\s*\|\s*", str(s))
        return [p.strip() for p in parts if p.strip()]

    albumartists = split_artists(albumartist_val)
    artists = split_artists(artist_val)

    if albumartists:
        albumartists_lower = {a.lower() for a in albumartists}
        remaining_artists = [a for a in artists if a.lower() not in albumartists_lower]
        final_artists = albumartists + remaining_artists
    else:
        final_artists = artists

    return "; ".join(final_artists)


def sanitize_path_component(val, fallback="Unknown"):
    if val is None:
        return fallback
    s = str(val).strip()
    if not s or s.lower() == "none":
        return fallback

    # basic cleanup
    s = re.sub(r'[<>"*?|/\\]', "_", s)
    s = s.replace(":", " -")

    s = s.strip()
    while s.endswith("."):
        s = s[:-1].strip()

    # handle windows reserved names
    if re.match(r"^(CON|PRN|AUX|NUL|COM\d|LPT\d)$", s, re.IGNORECASE):
        s = f"_{s}"

    return s if s else fallback


def format_track_prefix(tag) -> str:
    track_raw = str(tag.track or "").strip()

    # Match "Disc.Track" or "Disc-Track" (e.g. "1.01", "1-01")
    match_disc_track = re.match(r"^(\d+)[.\-](\d+)$", track_raw)
    if match_disc_track:
        disc_num = int(match_disc_track.group(1))
        track_num = int(match_disc_track.group(2))
        return f"{disc_num}-{track_num:02d}"

    # Match standard leading track digits (e.g. "01/12", "1")
    match_track = re.match(r"^\s*(\d+)", track_raw)
    track_num = int(match_track.group(1)) if match_track else 0

    try:
        disc_total = int(tag.disc_total) if tag.disc_total else 1
        disc_num = int(tag.disc) if tag.disc else 1
    except (ValueError, TypeError):
        disc_total, disc_num = 1, 1

    if disc_total > 1:
        return f"{disc_num}-{track_num:02d}"

    return f"{track_num:02d}"


def safe_rename(src: Path, dst: Path, dry_run: bool = False) -> bool:
    if str(src) == str(dst):
        return False

    if dry_run:
        logger.info(f"[DRY-RUN] Rename: {src} -> {dst}")
        return True

    is_case_only = src.parent == dst.parent and str(src).lower() == str(dst).lower()

    if dst.exists() and not is_case_only:
        logger.warning(f"Destination directory/file already exists: {dst}")
        return False

    try:
        if is_case_only:
            temp_path = src.with_name(f"{src.name}_tmp_rename")
            src.rename(temp_path)
            temp_path.rename(dst)
        else:
            src.rename(dst)
        return True
    except OSError as e:
        logger.error(f"Error renaming {src} to {dst}: {e}")
        return False


def process_library(library_dir, dry_run=False):
    # let it blow up if the root dir doesn't exist, user should know better
    albums = sorted(library_dir.iterdir())

    for album_path in albums:
        # album_path is a Path object representing the album directory
        album_dir = album_path
        if not album_dir.is_dir():
            continue

        entries = sorted(album_dir.iterdir())

        flac_files = [f for f in entries if f.is_file() and f.suffix.lower() == ".flac"]
        if not flac_files:
            continue

        first_flac = flac_files[0]
        try:
            tag = TinyTag.get(first_flac)
        except Exception as e:
            logger.error(f"Reading tags from {first_flac}: {e}")
            continue

        artist_combined = format_artists(tag.artist, tag.albumartist)
        artist = sanitize_path_component(artist_combined, fallback="Unknown Artist")
        album_name = sanitize_path_component(tag.album, fallback="Unknown Album")
        year = sanitize_path_component(extract_year(tag.year), fallback="0000")

        correct_album_directory = library_dir / f"{artist} - {album_name} ({year})"

        if str(album_dir) != str(correct_album_directory):
            logger.info(f"Renaming directory: {album_dir} -> {correct_album_directory}")
            if safe_rename(album_dir, correct_album_directory, dry_run=dry_run) and not dry_run:
                album_dir = correct_album_directory

        current_files = sorted(album_dir.iterdir())

        for file_path in current_files:
            if not file_path.is_file() or file_path.suffix.lower() != ".flac":
                continue

            try:
                tag = TinyTag.get(file_path)
            except Exception as e:
                logger.error(f"Reading tags from {file_path}: {e}")
                continue

            title = sanitize_path_component(tag.title, fallback="Unknown Title")
            track_str = format_track_prefix(tag)

            correct_track_filename = album_dir / f"{track_str} {title}.flac"
            if str(song_file_path) != str(correct_track_filename):
                logger.info(
                    f"Renaming file: {song_file_path.name} -> {correct_track_filename.name}"
                )
                safe_rename(song_file_path, correct_track_filename, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Rename FLAC folders and files to match their tags"
    )
    parser.add_argument("library_dir", type=Path, help="Path to the music library directory")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Preview changes")

    args = parser.parse_args()
    process_library(args.library_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
