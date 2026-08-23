"""Unit tests for machine-readable prompt template generation and configuration."""

import unittest
from src.config import AppConfig
from src.models import MoodProfile
from src.prompt import PromptTemplate, generate_recommendation_prompt


class TestPromptGeneration(unittest.TestCase):
    """Test suite for machine-readable song recommendation prompt generation."""

    def setUp(self):
        self.profile = MoodProfile(
            intensity=8,
            core_emotion="Joy",
            branch="Excited",
            specific_emotion="Energetic",
            code="J-3-1:8",
            intensity_label="Positive / Stable",
        )

    def test_json_prompt_rendering(self):
        config_json = AppConfig(song_count=10, output_format="json")
        prompt = generate_recommendation_prompt(self.profile, config=config_json)

        self.assertIn("Generate 10 songs based on the following mood profile.", prompt)
        self.assertIn("Intensity: 8", prompt)
        self.assertIn("Core Emotion: Joy", prompt)
        self.assertIn("Branch: Excited", prompt)
        self.assertIn("Specific Emotion: Energetic", prompt)
        self.assertIn("Mood Code: J-3-1:8", prompt)
        self.assertIn("Return the recommendations in JSON format", prompt)
        self.assertIn('"songs"', prompt)
        self.assertIn('"title"', prompt)
        self.assertIn('"artist"', prompt)
        self.assertIn("Return only valid JSON with no explanatory text or commentary.", prompt)

    def test_csv_prompt_rendering(self):
        config_csv = AppConfig(song_count=15, output_format="csv")
        prompt = generate_recommendation_prompt(self.profile, config=config_csv)

        self.assertIn("Generate 15 songs based on the following mood profile.", prompt)
        self.assertIn("Return the recommendations in CSV format with a header row.", prompt)
        self.assertIn("title,artist", prompt)
        self.assertIn("Return only CSV data with no explanatory text or commentary.", prompt)

    def test_yaml_prompt_rendering(self):
        config_yaml = AppConfig(song_count=20, output_format="yaml")
        prompt = generate_recommendation_prompt(self.profile, config=config_yaml)

        self.assertIn("Generate 20 songs based on the following mood profile.", prompt)
        self.assertIn("Return the recommendations in YAML format containing a list under a \"songs\" key.", prompt)
        self.assertIn("title:", prompt)
        self.assertIn("artist:", prompt)
        self.assertIn("Return only valid YAML with no explanatory text or commentary.", prompt)

    def test_singular_song_unit(self):
        config_1 = AppConfig(song_count=1, output_format="json")
        prompt_1 = generate_recommendation_prompt(self.profile, config=config_1)
        self.assertIn("Generate 1 song based on the following mood profile.", prompt_1)

    def test_unsupported_format_raises_error(self):
        tpl = PromptTemplate()
        with self.assertRaises(ValueError) as ctx:
            tpl.render(self.profile, song_count=5, output_format="unsupported_fmt")
        self.assertIn("Unsupported output format", str(ctx.exception))

    def test_custom_prompt_template_rendering(self):
        custom_tpl = PromptTemplate("Recommend {song_count} songs for [{code}] in {output_format} format.")
        rendered = custom_tpl.render(self.profile, song_count=5, output_format="custom")
        expected = "Recommend 5 songs for [J-3-1:8] in custom format."
        self.assertEqual(rendered, expected)

    def test_mood_profile_format(self):
        formatted = self.profile.format_profile()
        expected = (
            "Mood Profile\n"
            "-------------\n"
            "Intensity: 8\n"
            "Core Emotion: Joy\n"
            "Branch: Excited\n"
            "Specific Emotion: Energetic\n"
            "Mood Code: J-3-1:8"
        )
        self.assertEqual(formatted, expected)


if __name__ == "__main__":
    unittest.main()
