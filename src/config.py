"""Application configuration loader and validator."""

from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.json"


class ConfigError(ValueError):
    """Raised when application configuration is missing, malformed, or invalid."""
    pass


@dataclass(frozen=True)
class AppConfig:
    """Represents validated application configuration settings."""
    song_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "song_count": self.song_count,
        }


def validate_config(raw_data: Any) -> AppConfig:
    """Validate raw configuration data and return an AppConfig instance."""
    if not isinstance(raw_data, dict):
        raise ConfigError(f"Configuration root must be a JSON object, got {type(raw_data).__name__}.")

    if "song_count" not in raw_data:
        raise ConfigError("Missing required configuration field: 'song_count'.")

    song_count = raw_data["song_count"]

    if not isinstance(song_count, int) or isinstance(song_count, bool):
        raise ConfigError(f"Field 'song_count' must be an integer, got {type(song_count).__name__} ({song_count!r}).")

    if song_count <= 0:
        raise ConfigError(f"Field 'song_count' must be a positive integer (> 0), got {song_count}.")

    return AppConfig(song_count=song_count)


def load_config(config_path: Optional[Path | str] = None) -> AppConfig:
    """
    Load and validate configuration from the specified path or the default config.json.
    Raises ConfigError if the file is missing, cannot be parsed, or has invalid settings.
    """
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        raise ConfigError(f"Configuration file not found at: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Malformed JSON in configuration file '{path}': {e}") from e
    except Exception as e:
        raise ConfigError(f"Failed to read configuration file '{path}': {e}") from e

    return validate_config(raw_data)
