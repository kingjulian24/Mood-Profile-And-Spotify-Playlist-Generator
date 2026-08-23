"""Prompt template management and rendering for machine-readable song recommendations."""

from __future__ import annotations
from typing import Dict, Optional

from src.config import AppConfig, SUPPORTED_OUTPUT_FORMATS, load_config
from src.models import MoodProfile


JSON_PROMPT_TEMPLATE = (
    "Generate {song_count} {songs_unit} based on the following mood profile.\n\n"
    "Intensity: {intensity}\n"
    "Core Emotion: {core_emotion}\n"
    "Branch: {branch}\n"
    "Specific Emotion: {specific_emotion}\n"
    "Mood Code: {code}\n\n"
    "Return the recommendations in JSON format containing an array of objects under a \"songs\" key.\n"
    "Each object must contain exactly the following fields:\n"
    "- \"title\": string (song title)\n"
    "- \"artist\": string (artist name)\n\n"
    "Example format:\n"
    "{{\n"
    "  \"songs\": [\n"
    "    {{\n"
    "      \"title\": \"Song Title\",\n"
    "      \"artist\": \"Artist Name\"\n"
    "    }}\n"
    "  ]\n"
    "}}\n\n"
    "Return only valid JSON with no explanatory text or commentary."
)

CSV_PROMPT_TEMPLATE = (
    "Generate {song_count} {songs_unit} based on the following mood profile.\n\n"
    "Intensity: {intensity}\n"
    "Core Emotion: {core_emotion}\n"
    "Branch: {branch}\n"
    "Specific Emotion: {specific_emotion}\n"
    "Mood Code: {code}\n\n"
    "Return the recommendations in CSV format with a header row.\n"
    "The header must be exactly:\n"
    "title,artist\n\n"
    "Example format:\n"
    "title,artist\n"
    "Song Title,Artist Name\n\n"
    "Return only CSV data with no explanatory text or commentary."
)

YAML_PROMPT_TEMPLATE = (
    "Generate {song_count} {songs_unit} based on the following mood profile.\n\n"
    "Intensity: {intensity}\n"
    "Core Emotion: {core_emotion}\n"
    "Branch: {branch}\n"
    "Specific Emotion: {specific_emotion}\n"
    "Mood Code: {code}\n\n"
    "Return the recommendations in YAML format containing a list under a \"songs\" key.\n"
    "Each item must contain exactly the following fields:\n"
    "- title: string\n"
    "- artist: string\n\n"
    "Example format:\n"
    "songs:\n"
    "  - title: \"Song Title\"\n"
    "    artist: \"Artist Name\"\n\n"
    "Return only valid YAML with no explanatory text or commentary."
)

DEFAULT_FORMAT_TEMPLATES: Dict[str, str] = {
    "json": JSON_PROMPT_TEMPLATE,
    "csv": CSV_PROMPT_TEMPLATE,
    "yaml": YAML_PROMPT_TEMPLATE,
}


class PromptTemplate:
    """Manages format-specific prompt templates and renders them with a given MoodProfile."""

    def __init__(
        self,
        template: Optional[str] = None,
        format_templates: Optional[Dict[str, str]] = None,
    ):
        self._custom_template = template
        self._format_templates = dict(format_templates or DEFAULT_FORMAT_TEMPLATES)

    def render(
        self,
        profile: MoodProfile,
        song_count: int,
        output_format: str = "json",
    ) -> str:
        """Populate the prompt template deterministically using mood profile, song count, and output format."""
        normalized_format = output_format.strip().lower()
        if self._custom_template:
            template_str = self._custom_template
        elif normalized_format in self._format_templates:
            template_str = self._format_templates[normalized_format]
        else:
            raise ValueError(
                f"Unsupported output format '{output_format}'. Supported: {', '.join(SUPPORTED_OUTPUT_FORMATS)}"
            )

        songs_unit = "song" if song_count == 1 else "songs"
        return template_str.format(
            song_count=song_count,
            songs_unit=songs_unit,
            output_format=normalized_format,
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
    output_format: Optional[str] = None,
    config: Optional[AppConfig] = None,
    template: Optional[PromptTemplate] = None,
) -> str:
    """
    Render a recommendation prompt for a mood profile using configured or supplied settings.
    """
    cfg = config or load_config()
    resolved_count = song_count if song_count is not None else cfg.song_count
    resolved_format = output_format if output_format is not None else cfg.output_format

    t = template or PromptTemplate()
    return t.render(profile, song_count=resolved_count, output_format=resolved_format)
