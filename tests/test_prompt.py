"""Unit tests for prompt template management and dynamic configuration rendering."""

import unittest
from src.config import AppConfig
from src.models import MoodProfile
from src.prompt import PromptTemplate, generate_recommendation_prompt


class TestPromptGeneration(unittest.TestCase):
    """Test suite for song recommendation prompt generation with dynamic configuration."""

    def setUp(self):
        self.profile = MoodProfile(
            intensity=8,
            core_emotion="Joy",
            branch="Excited",
            specific_emotion="Energetic",
            code="J-3-1:8",
            intensity_label="Positive / Stable",
        )

    def test_default_prompt_rendering_with_config(self):
        config_10 = AppConfig(song_count=10)
        prompt = generate_recommendation_prompt(self.profile, config=config_10)

        self.assertIn("Generate 10 songs based on the following mood profile.", prompt)
        self.assertIn("Intensity: 8", prompt)
        self.assertIn("Core Emotion: Joy", prompt)
        self.assertIn("Branch: Excited", prompt)
        self.assertIn("Specific Emotion: Energetic", prompt)
        self.assertIn("Mood Code: J-3-1:8", prompt)
        self.assertIn("Return the song title and artist for each recommendation.", prompt)

    def test_prompt_rendering_with_custom_song_count(self):
        config_20 = AppConfig(song_count=20)
        prompt_20 = generate_recommendation_prompt(self.profile, config=config_20)
        self.assertIn("Generate 20 songs based on the following mood profile.", prompt_20)

        config_1 = AppConfig(song_count=1)
        prompt_1 = generate_recommendation_prompt(self.profile, config=config_1)
        self.assertIn("Generate 1 song based on the following mood profile.", prompt_1)

    def test_custom_prompt_template_rendering(self):
        custom_tpl = PromptTemplate("Recommend {song_count} songs for [{code}] {specific_emotion} at intensity {intensity}.")
        rendered = custom_tpl.render(self.profile, song_count=5)
        expected = "Recommend 5 songs for [J-3-1:8] Energetic at intensity 8."
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
