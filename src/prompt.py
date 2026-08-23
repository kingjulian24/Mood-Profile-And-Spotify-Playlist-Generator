"""Prompt template management and rendering for song recommendations."""

from __future__ import annotations
from typing import Optional
from src.models import MoodProfile


DEFAULT_PROMPT_TEMPLATE = (
    "Generate {song_count} song titles based on the following mood profile.\n\n"
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

    def render(self, profile: MoodProfile, song_count: int = 10) -> str:
        """Populate the prompt template deterministically using the provided mood profile."""
        return self.template.format(
            song_count=song_count,
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
    song_count: int = 10,
    template: Optional[PromptTemplate] = None,
) -> str:
    """Convenience function to render a recommendation prompt for a mood profile."""
    t = template or PromptTemplate()
    return t.render(profile, song_count=song_count)
