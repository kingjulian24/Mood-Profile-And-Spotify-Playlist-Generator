"""Tests for MoodSelectionCLI interactive workflow."""

import unittest
from typing import List

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
    """Test suite for interactive CLI mood selection."""

    def setUp(self):
        self.taxonomy = MoodTaxonomy()

    def test_full_successful_flow(self):
        # Steps:
        # 1: Core Emotion (1 = Joy)
        # 2: Branch (3 = Excited)
        # 3: Specific Emotion (1 = Energetic)
        # 4: Intensity (8)
        # 5: Confirm (c)
        inputs = ["1", "3", "1", "8", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()

        self.assertIsNotNone(selection)
        self.assertEqual(selection.core_emotion, "Joy")
        self.assertEqual(selection.branch, "Excited")
        self.assertEqual(selection.specific_emotion, "Energetic")
        self.assertEqual(selection.intensity, 8)
        self.assertEqual(selection.code, "J-3-1:8")

    def test_invalid_input_handling_and_reprompt(self):
        # Steps with invalid inputs:
        # Core: "invalid", "99", then "1" (Joy)
        # Branch: "abc", "0", then "2" (Happy)
        # Specific: "9", then "1" (Blissful)
        # Intensity: "15", "-1", then "7"
        # Confirmation: "c"
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
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()

        self.assertIsNotNone(selection)
        self.assertEqual(selection.core_emotion, "Joy")
        self.assertEqual(selection.branch, "Happy")
        self.assertEqual(selection.specific_emotion, "Blissful")
        self.assertEqual(selection.intensity, 7)
        self.assertEqual(selection.code, "J-2-1:7")

    def test_back_navigation(self):
        # Step 1: Core (2 = Sadness)
        # Step 2: 'b' (go back to Step 1)
        # Step 1: Core (1 = Joy)
        # Step 2: Branch (3 = Excited)
        # Step 3: 'b' (go back to Step 2)
        # Step 2: Branch (1 = Content)
        # Step 3: Specific (2 = Satisfied)
        # Step 4: Intensity (5)
        # Step 5: Confirm (c)
        inputs = ["2", "b", "1", "3", "b", "1", "2", "5", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()

        self.assertIsNotNone(selection)
        self.assertEqual(selection.core_emotion, "Joy")
        self.assertEqual(selection.branch, "Content")
        self.assertEqual(selection.specific_emotion, "Satisfied")
        self.assertEqual(selection.intensity, 5)
        self.assertEqual(selection.code, "J-1-2:5")

    def test_restart_flow(self):
        # Initial: 1 -> 3 -> 1 -> 8
        # At summary: 'r' (restart)
        # New selection: 3 (Anger) -> 1 (Irritated) -> 2 (Frustrated) -> 6 -> 'c'
        inputs = ["1", "3", "1", "8", "r", "3", "1", "2", "6", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()

        self.assertIsNotNone(selection)
        self.assertEqual(selection.core_emotion, "Anger")
        self.assertEqual(selection.branch, "Irritated")
        self.assertEqual(selection.specific_emotion, "Frustrated")
        self.assertEqual(selection.intensity, 6)
        self.assertEqual(selection.code, "A-1-2:6")

    def test_edit_step_flow(self):
        # Initial: 1 (Joy) -> 3 (Excited) -> 1 (Energetic) -> 8
        # At summary: 'e' (edit) -> 4 (Intensity) -> 10 -> 'c'
        inputs = ["1", "3", "1", "8", "e", "4", "10", "c"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()

        self.assertIsNotNone(selection)
        self.assertEqual(selection.core_emotion, "Joy")
        self.assertEqual(selection.branch, "Excited")
        self.assertEqual(selection.specific_emotion, "Energetic")
        self.assertEqual(selection.intensity, 10)
        self.assertEqual(selection.code, "J-3-1:10")

    def test_quit_cancellation(self):
        inputs = ["q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        selection = cli.run()
        self.assertIsNone(selection)


if __name__ == "__main__":
    unittest.main()
