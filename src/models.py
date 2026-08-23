"""Data models for structured mood representation, song parsing, and Spotify playlist generation."""

from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class IntensityLevel:
    """Represents an intensity level bracket."""
    range: List[int]
    label: str
    description: str


@dataclass(frozen=True)
class Branch:
    """Represents a branch in the mood taxonomy."""
    name: str
    description: str
    specific_emotions: List[str]


@dataclass(frozen=True)
class CoreEmotion:
    """Represents a top-level core emotion in the mood taxonomy."""
    name: str
    code_letter: str
    description: str
    branches: Dict[str, Branch]


@dataclass
class MoodProfile:
    """Structured representation of a user's selected mood profile."""
    intensity: int
    core_emotion: str
    branch: str
    specific_emotion: str
    code: str
    intensity_label: str = ""
    intensity_description: str = ""
    core_index: int = 1
    branch_index: int = 1
    specific_index: int = 1

    def format_profile(self) -> str:
        """Format the mood profile summary block."""
        return (
            "Mood Profile\n"
            "-------------\n"
            f"Intensity: {self.intensity}\n"
            f"Core Emotion: {self.core_emotion}\n"
            f"Branch: {self.branch}\n"
            f"Specific Emotion: {self.specific_emotion}\n"
            f"Mood Code: {self.code}"
        )

    def format_playlist_name(self, timestamp: Optional[datetime] = None) -> str:
        """Generate a canonical Spotify playlist name based on the mood hierarchy and timestamp."""
        dt = timestamp or datetime.now()
        time_str = dt.strftime("%I:%M %p").lstrip("0")
        date_str = f"{dt.strftime('%b')} {dt.day}, {dt.year}"
        return f"{self.core_emotion} — {self.branch} — {self.specific_emotion} — {date_str} {time_str}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert the mood profile to a dictionary matching the schema."""
        return {
            "intensity": self.intensity,
            "core_emotion": self.core_emotion,
            "branch": self.branch,
            "specific_emotion": self.specific_emotion,
            "code": self.code,
            "intensity_label": self.intensity_label,
            "intensity_description": self.intensity_description,
            "taxonomy_path": {
                "core_index": self.core_index,
                "branch_index": self.branch_index,
                "specific_index": self.specific_index,
                "core_emotion": self.core_emotion,
                "branch": self.branch,
                "specific_emotion": self.specific_emotion,
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert the mood profile to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


# Alias for backward compatibility
MoodSelection = MoodProfile


@dataclass(frozen=True)
class SongRecommendation:
    """Represents a song recommendation parsed from external chatbot output."""
    title: str
    artist: str

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise ValueError("Song title cannot be empty.")
        if not self.artist or not self.artist.strip():
            raise ValueError("Song artist cannot be empty.")


@dataclass(frozen=True)
class ResolvedTrack:
    """Represents a song recommendation successfully resolved against the Spotify catalog."""
    title: str
    artist: str
    spotify_uri: str
    spotify_id: str
    spotify_url: str = ""
    album_name: str = ""


@dataclass(frozen=True)
class UnresolvedTrack:
    """Represents a song recommendation that could not be resolved on Spotify."""
    title: str
    artist: str
    reason: str


@dataclass
class PlaylistResult:
    """Result of creating a Spotify playlist from resolved tracks."""
    playlist_id: str
    playlist_name: str
    playlist_url: str
    resolved_tracks: List[ResolvedTrack] = field(default_factory=list)
    unresolved_tracks: List[UnresolvedTrack] = field(default_factory=list)

    @property
    def total_recommendations(self) -> int:
        return len(self.resolved_tracks) + len(self.unresolved_tracks)

    @property
    def success_count(self) -> int:
        return len(self.resolved_tracks)

    @property
    def unresolved_count(self) -> int:
        return len(self.unresolved_tracks)
