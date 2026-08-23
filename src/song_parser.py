"""Parsers for machine-readable song recommendation outputs (JSON, CSV, YAML)."""

from __future__ import annotations
import csv
import io
import json
import re
from typing import Any, Dict, List, Optional

from src.models import SongRecommendation


class SongParseError(ValueError):
    """Raised when song recommendations cannot be parsed from the supplied text."""
    pass


def _strip_markdown_fences(raw_text: str) -> str:
    """Remove leading/trailing markdown code fences (e.g. ```json ... ```)."""
    text = raw_text.strip()
    if text.startswith("```"):
        # Match ```lang ... ```
        match = re.match(r"^```[a-zA-Z0-9_-]*\n?(.*?)\n?```$", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: remove first line if ``` and last line if ```
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
            return "\n".join(lines[1:-1]).strip()
    return text


def _clean_cell(cell: str) -> str:
    """Strip whitespace and outer surrounding quotes."""
    return cell.strip().strip("'\"")


def _parse_json(text: str) -> List[SongRecommendation]:
    """Parse song recommendations from JSON string."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise SongParseError(f"Invalid JSON format: {e}") from e

    items: List[Any] = []
    if isinstance(data, dict):
        if "songs" in data and isinstance(data["songs"], list):
            items = data["songs"]
        elif "recommendations" in data and isinstance(data["recommendations"], list):
            items = data["recommendations"]
        else:
            raise SongParseError("JSON object must contain a 'songs' array.")
    elif isinstance(data, list):
        items = data
    else:
        raise SongParseError("JSON must be an object with a 'songs' list or a direct list of songs.")

    if not items:
        raise SongParseError("No songs found in the supplied JSON.")

    songs: List[SongRecommendation] = []
    for idx, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise SongParseError(f"Song item #{idx} is not a valid object: {item!r}")
        title = item.get("title") or item.get("song") or item.get("name")
        artist = item.get("artist") or item.get("band") or item.get("performer")

        if not title or not isinstance(title, str) or not title.strip():
            raise SongParseError(f"Song item #{idx} is missing a valid 'title' field.")
        if not artist or not isinstance(artist, str) or not artist.strip():
            raise SongParseError(f"Song item #{idx} is missing a valid 'artist' field.")

        songs.append(SongRecommendation(title=title.strip(), artist=artist.strip()))

    return songs


def _parse_csv(text: str) -> List[SongRecommendation]:
    """Parse song recommendations from CSV string."""
    # Dedent and clean lines
    cleaned_lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not cleaned_lines:
        raise SongParseError("Supplied CSV is empty.")

    reader = csv.reader(io.StringIO("\n".join(cleaned_lines)), skipinitialspace=True)
    rows = [row for row in reader if row and any(cell.strip() for cell in row)]

    if not rows:
        raise SongParseError("Supplied CSV is empty.")

    header = [_clean_cell(col).lower() for col in rows[0]]
    if "title" not in header or "artist" not in header:
        raise SongParseError(f"CSV header must contain 'title' and 'artist' columns. Found: {header}")

    title_idx = header.index("title")
    artist_idx = header.index("artist")
    data_rows = rows[1:]

    if not data_rows:
        raise SongParseError("No song records found in CSV.")

    songs: List[SongRecommendation] = []
    for idx, row in enumerate(data_rows, 1):
        if len(row) <= max(title_idx, artist_idx):
            raise SongParseError(f"CSV row #{idx} has insufficient columns: {row}")
        title = _clean_cell(row[title_idx])
        artist = _clean_cell(row[artist_idx])
        if not title:
            raise SongParseError(f"CSV row #{idx} has an empty 'title'.")
        if not artist:
            raise SongParseError(f"CSV row #{idx} has an empty 'artist'.")
        songs.append(SongRecommendation(title=title, artist=artist))

    return songs


def _parse_simple_yaml(text: str) -> List[SongRecommendation]:
    """
    Lightweight, robust YAML parser for song recommendation lists.
    Handles standard YAML list of objects with title and artist.
    """
    lines = text.strip().splitlines()
    songs: List[SongRecommendation] = []
    current_song: Dict[str, str] = {}

    def _flush_song():
        if current_song:
            title = current_song.get("title", "").strip()
            artist = current_song.get("artist", "").strip()
            if not title:
                raise SongParseError(f"Incomplete YAML song entry (missing title): {current_song}")
            if not artist:
                raise SongParseError(f"Incomplete YAML song entry (missing artist): {current_song}")
            songs.append(SongRecommendation(title=title, artist=artist))
            current_song.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in ("songs:", "recommendations:", "---"):
            continue

        # Item marker: "- title: ..." or "- artist: ..." or "-"
        if stripped.startswith("-"):
            _flush_song()
            rest = stripped[1:].strip()
            if rest:
                if ":" in rest:
                    k, v = rest.split(":", 1)
                    k_clean = _clean_cell(k).lower()
                    v_clean = _clean_cell(v)
                    if k_clean in ("title", "artist"):
                        current_song[k_clean] = v_clean
            continue

        # Key-value line inside current item
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            k_clean = _clean_cell(k).lower()
            v_clean = _clean_cell(v)
            if k_clean in ("title", "artist"):
                current_song[k_clean] = v_clean

    _flush_song()

    if not songs:
        raise SongParseError("No valid songs could be parsed from YAML input.")

    return songs


def parse_song_list(
    raw_input: str,
    format_hint: Optional[str] = None,
) -> List[SongRecommendation]:
    """
    Parse a machine-readable song recommendation output into a list of SongRecommendation objects.
    Automatically strips markdown fences and uses format_hint if provided (json, csv, yaml).
    If no format_hint is given or parsing fails with format_hint, attempts auto-detection.
    """
    cleaned = _strip_markdown_fences(raw_input)
    if not cleaned:
        raise SongParseError("Input song list is empty.")

    hint = (format_hint or "").strip().lower()

    if hint == "json" or (not hint and (cleaned.startswith("{") or cleaned.startswith("["))):
        try:
            return _parse_json(cleaned)
        except SongParseError:
            if hint == "json":
                raise

    if hint == "csv" or (not hint and ("title,artist" in cleaned.lower() or "artist,title" in cleaned.lower())):
        try:
            return _parse_csv(cleaned)
        except SongParseError:
            if hint == "csv":
                raise

    if hint == "yaml" or (not hint and ("songs:" in cleaned or "- title:" in cleaned or "- artist:" in cleaned)):
        try:
            return _parse_simple_yaml(cleaned)
        except SongParseError:
            if hint == "yaml":
                raise

    # Auto-detection fallback order: JSON -> CSV -> YAML
    for parser_fn in (_parse_json, _parse_csv, _parse_simple_yaml):
        try:
            return parser_fn(cleaned)
        except Exception:
            continue

    raise SongParseError(
        "Could not parse song list. Please ensure the input matches the configured JSON, CSV, or YAML format."
    )
