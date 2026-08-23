"""Unit tests for prompt template management and rendering."""

import unittest
from src.models import MoodProfile
from src.prompt import PromptTemplate, generate_recommendation_prompt


class TestPromptGeneration(unittest.TestCase):
    """Test suite for song recommendation prompt generation."""

    def setUp(self):
        self.profile = MoodProfile(
            intensity=8,
            core_emotion="Joy",
            branch="Excited",
            specific_emotion="Energetic",
            code="J-3-1:8",
            intensity_label="Positive / Stable",
        )

    def test_default_prompt_template_rendering(self):
        prompt = generate_recommendation_prompt(self.profile, song_count=10)

        # Verify all mood profile fields are present
        self.assertIn("Generate 10 song titles based on the following mood profile.", prompt)
        self.assertIn("Intensity: 8", prompt)
        self.assertIn("Core Emotion: Joy", prompt)
        self.assertIn("Branch: Excited", prompt)
        self.assertIn("Specific Emotion: Energetic", prompt)
        self.assertIn("Mood Code: J-3-1:8", prompt)
        self.assertIn("Return the song title and artist for each recommendation.", prompt)

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
