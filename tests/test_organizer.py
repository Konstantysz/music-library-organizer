from types import SimpleNamespace
from music_library_organizer import (
    extract_year,
    format_artists,
    format_track_prefix,
    sanitize_path_component,
    safe_rename,
)


def test_extract_year():
    assert extract_year("2025-04-04") == "2025"
    assert extract_year("1999") == "1999"
    assert extract_year(2021) == "2021"
    assert extract_year(None) == "0000"
    assert extract_year("") == "0000"
    assert extract_year("Unknown") == "0000"


def test_format_artists():
    assert format_artists("Artist A", "Artist A") == "Artist A"
    assert format_artists("Feature B", "Main Artist") == "Main Artist; Feature B"
    assert format_artists("Artist 1; Artist 2", None) == "Artist 1; Artist 2"
    assert format_artists(None, None) == "Unknown Artist"


def test_sanitize_path_component():
    assert sanitize_path_component("Album: Subtitle?") == "Album - Subtitle"
    bad_chars = "Illegal / \\ * < > | characters"
    assert sanitize_path_component(bad_chars) == "Illegal _ _    _ characters"
    assert sanitize_path_component("Trailing dots...") == "Trailing dots"
    assert sanitize_path_component("CON") == "_CON"
    assert sanitize_path_component(None) == "Unknown"
    assert sanitize_path_component("None") == "Unknown"
    assert sanitize_path_component("") == "Unknown"


def test_format_track_prefix():
    # Test "1.01" track tag format
    tag_dot = SimpleNamespace(track="1.01", disc=None, disc_total=None)
    assert format_track_prefix(tag_dot) == "1-01"

    # Test "1-02" track tag format
    tag_dash = SimpleNamespace(track="1-02", disc=None, disc_total=None)
    assert format_track_prefix(tag_dash) == "1-02"

    # Test "01/12" track tag format
    tag_slash = SimpleNamespace(track="01/12", disc="1", disc_total="1")
    assert format_track_prefix(tag_slash) == "01"

    # Test multi-disc tag format
    tag_multi = SimpleNamespace(track="3", disc="2", disc_total="2")
    assert format_track_prefix(tag_multi) == "2-03"


def test_safe_rename_dry_run(tmp_path):
    src = tmp_path / "old_name.txt"
    dst = tmp_path / "new_name.txt"
    src.write_text("test")

    renamed = safe_rename(src, dst, dry_run=True)
    assert renamed is True
    assert src.exists()
    assert not dst.exists()
