"""Tests for MoodSelectionCLI interactive workflow and prompt generation."""

import unittest
from typing import List

from src.config import AppConfig
from src.mood_selection import MoodSelectionCLI
from src.taxonomy import MoodTaxonomy


class MockCLIHelper:
    """Helper to simulate interactive user input and capture output."""

    def __init__(self, inputs: List[str]):
        self.inputs = list(inputs)
        self.outputs: List[str] = []

    def mock_input(self, prompt: str = "") -> str:
        if not self.inputs:
            raise EOFError("No more mock inputs provided.")
        val = self.inputs.pop(0)
        self.outputs.append(f"{prompt}{val}")
        return val

    def mock_print(self, msg: str = "") -> None:
        self.outputs.append(msg)


class TestMoodSelectionCLI(unittest.TestCase):
    """Test suite for interactive CLI mood selection and prompt output."""

    def setUp(self):
        self.taxonomy = MoodTaxonomy()
        self.config = AppConfig(song_count=10)

    def test_full_successful_flow_generates_profile_and_prompt(self):
        # Steps:
        # 1: Core Emotion (1 = Joy)
        # 2: Branch (3 = Excited)
        # 3: Specific Emotion (1 = Energetic)
        # 4: Intensity (8)
        # 5: Confirm & Generate Prompt (c)
        inputs = ["1", "3", "1", "8", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()

        self.assertIsNotNone(result)
        profile, prompt = result
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Excited")
        self.assertEqual(profile.specific_emotion, "Energetic")
        self.assertEqual(profile.intensity, 8)
        self.assertEqual(profile.code, "J-3-1:8")

        # Verify generated prompt
        self.assertIn("Generate 10 songs based on the following mood profile.", prompt)
        self.assertIn("Intensity: 8", prompt)
        self.assertIn("Mood Code: J-3-1:8", prompt)

    def test_custom_song_count_in_cli(self):
        custom_config = AppConfig(song_count=20)
        inputs = ["1", "3", "1", "8", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=custom_config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()
        self.assertIsNotNone(result)
        _, prompt = result
        self.assertIn("Generate 20 songs based on the following mood profile.", prompt)

    def test_invalid_input_handling_and_reprompt(self):
        inputs = [
            "invalid", "99", "1",
            "abc", "0", "2",
            "9", "1",
            "15", "-1", "7",
            "c",
        ]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()

        self.assertIsNotNone(result)
        profile, prompt = result
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Happy")
        self.assertEqual(profile.specific_emotion, "Blissful")
        self.assertEqual(profile.intensity, 7)
        self.assertEqual(profile.code, "J-2-1:7")

    def test_back_navigation(self):
        inputs = ["2", "b", "1", "3", "b", "1", "2", "5", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()

        self.assertIsNotNone(result)
        profile, _ = result
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Content")
        self.assertEqual(profile.specific_emotion, "Satisfied")
        self.assertEqual(profile.intensity, 5)
        self.assertEqual(profile.code, "J-1-2:5")

    def test_restart_flow(self):
        inputs = ["1", "3", "1", "8", "r", "3", "1", "2", "6", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()

        self.assertIsNotNone(result)
        profile, prompt = result
        self.assertEqual(profile.core_emotion, "Anger")
        self.assertEqual(profile.branch, "Irritated")
        self.assertEqual(profile.specific_emotion, "Frustrated")
        self.assertEqual(profile.intensity, 6)
        self.assertEqual(profile.code, "A-1-2:6")
        self.assertIn("Mood Code: A-1-2:6", prompt)

    def test_edit_step_flow(self):
        inputs = ["1", "3", "1", "8", "e", "4", "10", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()

        self.assertIsNotNone(result)
        profile, prompt = result
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Excited")
        self.assertEqual(profile.specific_emotion, "Energetic")
        self.assertEqual(profile.intensity, 10)
        self.assertEqual(profile.code, "J-3-1:10")
        self.assertIn("Intensity: 10", prompt)

    def test_quit_cancellation(self):
        inputs = ["q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
