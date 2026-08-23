"""Taxonomy loader, navigator, and code parser based on context/mood-taxonomy.json."""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.models import Branch, CoreEmotion, IntensityLevel, MoodSelection


DEFAULT_TAXONOMY_PATH = Path(__file__).parent.parent / "context" / "mood-taxonomy.json"

# Canonical prefix codes for core emotions
CORE_EMOTION_CODES: Dict[str, str] = {
    "Joy": "J",
    "Sadness": "S",
    "Anger": "A",
    "Fear": "F",
    "Disgust": "D",
    "Surprise": "Su",
}

# Reverse mapping for code lookup
CODE_TO_CORE_EMOTION: Dict[str, str] = {
    code: name for name, code in CORE_EMOTION_CODES.items()
}
# Also allow single letter 'U' or 'X' or 'Sp' for Surprise if parsed
CODE_TO_CORE_EMOTION.update({"Sp": "Surprise", "U": "Surprise", "X": "Surprise"})


class MoodTaxonomy:
    """Provides dynamic traversal, validation, and encoding of the canonical mood taxonomy."""

    def __init__(self, taxonomy_path: Optional[Path | str] = None):
        self.taxonomy_path = Path(taxonomy_path) if taxonomy_path else DEFAULT_TAXONOMY_PATH
        self._raw_data: Dict[str, Any] = {}
        self._intensity_levels: List[IntensityLevel] = []
        self._core_emotions: Dict[str, CoreEmotion] = {}
        self._core_emotion_list: List[str] = []
        self._load()

    def _load(self) -> None:
        """Load and parse the JSON taxonomy source of truth."""
        if not self.taxonomy_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found at: {self.taxonomy_path}")

        with open(self.taxonomy_path, "r", encoding="utf-8") as f:
            self._raw_data = json.load(f)

        # Parse intensity levels
        intensity_data = self._raw_data.get("intensity_scale", {})
        self.intensity_min: int = intensity_data.get("min", 1)
        self.intensity_max: int = intensity_data.get("max", 10)
        self.intensity_scale_description: str = intensity_data.get("description", "")

        self._intensity_levels = [
            IntensityLevel(
                range=lvl["range"],
                label=lvl["label"],
                description=lvl["description"],
            )
            for lvl in intensity_data.get("levels", [])
        ]

        # Parse core emotions and their branches
        tax_dict = self._raw_data.get("taxonomy", {})
        self._core_emotion_list = list(tax_dict.keys())

        for core_name, core_val in tax_dict.items():
            code_letter = CORE_EMOTION_CODES.get(core_name, core_name[0].upper())
            branches_dict: Dict[str, Branch] = {}
            for b_name, b_val in core_val.get("branches", {}).items():
                branches_dict[b_name] = Branch(
                    name=b_name,
                    description=b_val.get("description", ""),
                    specific_emotions=list(b_val.get("specific_emotions", [])),
                )
            self._core_emotions[core_name] = CoreEmotion(
                name=core_name,
                code_letter=code_letter,
                description=core_val.get("description", ""),
                branches=branches_dict,
            )

    @property
    def core_emotions(self) -> List[str]:
        """Return the list of core emotion names in order."""
        return list(self._core_emotion_list)

    def get_core_emotion(self, name_or_index: str | int) -> CoreEmotion:
        """Retrieve CoreEmotion by name or 1-based index."""
        if isinstance(name_or_index, int):
            if not 1 <= name_or_index <= len(self._core_emotion_list):
                raise IndexError(f"Core emotion index {name_or_index} out of range (1..{len(self._core_emotion_list)})")
            name = self._core_emotion_list[name_or_index - 1]
        else:
            name = name_or_index

        if name not in self._core_emotions:
            raise KeyError(f"Core emotion '{name}' not found in taxonomy.")
        return self._core_emotions[name]

    def get_branches(self, core_emotion: str | int) -> List[str]:
        """Return list of branch names for the specified core emotion."""
        core = self.get_core_emotion(core_emotion)
        return list(core.branches.keys())

    def get_branch(self, core_emotion: str | int, branch_name_or_index: str | int) -> Branch:
        """Retrieve Branch by name or 1-based index under a core emotion."""
        core = self.get_core_emotion(core_emotion)
        branch_names = list(core.branches.keys())

        if isinstance(branch_name_or_index, int):
            if not 1 <= branch_name_or_index <= len(branch_names):
                raise IndexError(f"Branch index {branch_name_or_index} out of range (1..{len(branch_names)})")
            b_name = branch_names[branch_name_or_index - 1]
        else:
            b_name = branch_name_or_index

        if b_name not in core.branches:
            raise KeyError(f"Branch '{b_name}' not found under core emotion '{core.name}'.")
        return core.branches[b_name]

    def get_specific_emotions(self, core_emotion: str | int, branch: str | int) -> List[str]:
        """Return list of specific emotions for a given core emotion and branch."""
        b = self.get_branch(core_emotion, branch)
        return list(b.specific_emotions)

    def get_specific_emotion(
        self, core_emotion: str | int, branch: str | int, specific_name_or_index: str | int
    ) -> str:
        """Retrieve specific emotion by name or 1-based index."""
        b = self.get_branch(core_emotion, branch)
        if isinstance(specific_name_or_index, int):
            if not 1 <= specific_name_or_index <= len(b.specific_emotions):
                raise IndexError(
                    f"Specific emotion index {specific_name_or_index} out of range (1..{len(b.specific_emotions)})"
                )
            return b.specific_emotions[specific_name_or_index - 1]

        if specific_name_or_index not in b.specific_emotions:
            raise KeyError(f"Specific emotion '{specific_name_or_index}' not found under branch '{b.name}'.")
        return specific_name_or_index

    def get_intensity_info(self, intensity: int) -> Tuple[str, str]:
        """Return (label, description) for a given intensity value (1..10)."""
        if not self.intensity_min <= intensity <= self.intensity_max:
            raise ValueError(f"Intensity {intensity} out of valid range ({self.intensity_min}..{self.intensity_max})")

        for level in self._intensity_levels:
            if level.range[0] <= intensity <= level.range[1]:
                return level.label, level.description

        return "Unknown", ""

    def get_intensity_levels(self) -> List[IntensityLevel]:
        """Return the list of configured intensity level ranges and descriptions."""
        return list(self._intensity_levels)

    def build_mood_selection(
        self,
        core_index: int,
        branch_index: int,
        specific_index: int,
        intensity: int,
    ) -> MoodSelection:
        """Construct a validated MoodSelection object from 1-based hierarchy indices and intensity."""
        core = self.get_core_emotion(core_index)
        branch = self.get_branch(core.name, branch_index)
        specific = self.get_specific_emotion(core.name, branch.name, specific_index)

        if not self.intensity_min <= intensity <= self.intensity_max:
            raise ValueError(f"Intensity must be between {self.intensity_min} and {self.intensity_max}, got {intensity}.")

        label, desc = self.get_intensity_info(intensity)
        code = f"{core.code_letter}-{branch_index}-{specific_index}:{intensity}"

        return MoodSelection(
            core_emotion=core.name,
            branch=branch.name,
            specific_emotion=specific,
            intensity=intensity,
            code=code,
            intensity_label=label,
            intensity_description=desc,
            core_index=core_index,
            branch_index=branch_index,
            specific_index=specific_index,
        )

    def build_from_names(
        self,
        core_emotion: str,
        branch: str,
        specific_emotion: str,
        intensity: int,
    ) -> MoodSelection:
        """Construct a validated MoodSelection from emotion names and intensity."""
        if core_emotion not in self._core_emotion_list:
            raise KeyError(f"Core emotion '{core_emotion}' is not valid.")
        core_idx = self._core_emotion_list.index(core_emotion) + 1

        branches = self.get_branches(core_emotion)
        if branch not in branches:
            raise KeyError(f"Branch '{branch}' is not valid for '{core_emotion}'.")
        branch_idx = branches.index(branch) + 1

        specifics = self.get_specific_emotions(core_emotion, branch)
        if specific_emotion not in specifics:
            raise KeyError(f"Specific emotion '{specific_emotion}' is not valid for branch '{branch}'.")
        specific_idx = specifics.index(specific_emotion) + 1

        return self.build_mood_selection(core_idx, branch_idx, specific_idx, intensity)

    def parse_code(self, code_str: str) -> MoodSelection:
        """
        Parse a mood code formatted like 'J-3-1:8' or 'Joy-3-1:8' into a MoodSelection object.
        """
        raw = code_str.strip()
        if ":" not in raw:
            raise ValueError(f"Invalid mood code format (missing intensity delimiter ':'): '{code_str}'")

        path_part, intensity_part = raw.split(":", 1)
        try:
            intensity = int(intensity_part.strip())
        except ValueError:
            raise ValueError(f"Invalid intensity in mood code: '{intensity_part}'")

        path_tokens = path_part.split("-")
        if len(path_tokens) != 3:
            raise ValueError(f"Invalid path structure in mood code (expected CORE-BRANCH-SPECIFIC): '{path_part}'")

        core_token, branch_token, specific_token = path_tokens

        # Resolve core emotion
        core_token_clean = core_token.strip()
        if core_token_clean in CODE_TO_CORE_EMOTION:
            core_name = CODE_TO_CORE_EMOTION[core_token_clean]
            core_idx = self._core_emotion_list.index(core_name) + 1
        elif core_token_clean in self._core_emotion_list:
            core_name = core_token_clean
            core_idx = self._core_emotion_list.index(core_name) + 1
        else:
            raise ValueError(f"Unknown core emotion code/token: '{core_token_clean}'")

        try:
            branch_idx = int(branch_token.strip())
            specific_idx = int(specific_token.strip())
        except ValueError:
            raise ValueError(f"Branch and specific indices must be integers in code '{code_str}'")

        return self.build_mood_selection(core_idx, branch_idx, specific_idx, intensity)
