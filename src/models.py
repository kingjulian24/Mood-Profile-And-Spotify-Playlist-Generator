"""Data models for structured mood representation and taxonomy navigation."""

from __future__ import annotations
import json
from dataclasses import asdict, dataclass, field
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
class MoodSelection:
    """Structured representation of a user's selected mood and intensity."""
    core_emotion: str
    branch: str
    specific_emotion: str
    intensity: int
    code: str
    intensity_label: str = ""
    intensity_description: str = ""
    core_index: int = 1
    branch_index: int = 1
    specific_index: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert the mood selection to a dictionary matching application schemas."""
        return {
            "code": self.code,
            "intensity": self.intensity,
            "core_emotion": self.core_emotion,
            "branch": self.branch,
            "specific_emotion": self.specific_emotion,
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
        """Convert the mood selection to a formatted JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def format_tree(self) -> str:
        """Render a formatted ASCII hierarchy tree of the selected mood."""
        return (
            f"{self.core_emotion}\n"
            f"└── {self.branch}\n"
            f"    └── {self.specific_emotion}\n\n"
            f"Intensity: {self.intensity}/10 ({self.intensity_label})\n"
            f"Mood Code: {self.code}"
        )
