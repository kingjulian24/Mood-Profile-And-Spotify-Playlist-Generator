"""Prompt template management and rendering for song recommendations."""

from __future__ import annotations
from typing import Optional

from src.config import AppConfig, load_config
from src.models import MoodProfile


DEFAULT_PROMPT_TEMPLATE = (
    "Generate {song_count} {songs_unit} based on the following mood profile.\n\n"
    "Intensity: {intensity}\n"
    "Core Emotion: {core_emotion}\n"
    "Branch: {branch}\n"
    "Specific Emotion: {specific_emotion}\n"
    "Mood Code: {code}\n\n"
    "Return the song title and artist for each recommendation."
)


class PromptTemplate:
    """Manages static prompt templates and renders them with a given MoodProfile."""

    def __init__(self, template: str = DEFAULT_PROMPT_TEMPLATE):
        self.template = template

    def render(self, profile: MoodProfile, song_count: int) -> str:
        """Populate the prompt template deterministically using the provided mood profile and song count."""
        songs_unit = "song" if song_count == 1 else "songs"
        return self.template.format(
            song_count=song_count,
            songs_unit=songs_unit,
            intensity=profile.intensity,
            core_emotion=profile.core_emotion,
            branch=profile.branch,
            specific_emotion=profile.specific_emotion,
            code=profile.code,
            intensity_label=profile.intensity_label,
            intensity_description=profile.intensity_description,
        )


def generate_recommendation_prompt(
    profile: MoodProfile,
    song_count: Optional[int] = None,
    config: Optional[AppConfig] = None,
    template: Optional[PromptTemplate] = None,
) -> str:
    """
    Render a recommendation prompt for a mood profile using configured or supplied song count.
    If song_count is not provided, it resolves song_count from config or loads the application configuration.
    """
    if song_count is None:
        cfg = config or load_config()
        resolved_count = cfg.song_count
    else:
        resolved_count = song_count

    t = template or PromptTemplate()
    return t.render(profile, song_count=resolved_count)
