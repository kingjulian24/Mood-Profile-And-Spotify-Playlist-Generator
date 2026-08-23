"""Tests for MoodSelectionCLI interactive workflow, prompt generation, and Spotify playlist creation."""

import unittest
from typing import List

from src.config import AppConfig
from src.models import MoodProfile, ResolvedTrack
from src.mood_selection import MoodSelectionCLI
from src.spotify import SpotifyClient
from src.taxonomy import MoodTaxonomy
from tests.test_spotify import MockSpotifyHTTPRequester


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
    """Test suite for interactive CLI mood selection, prompt output, and playlist import."""

    def setUp(self):
        self.taxonomy = MoodTaxonomy()
        self.config = AppConfig(song_count=10, output_format="json")
        self.mock_http = MockSpotifyHTTPRequester()
        self.spotify_client = SpotifyClient(
            access_token="test_valid_access_token",
            http_requester=self.mock_http,
        )

    def test_full_successful_flow_generates_profile_and_prompt(self):
        # Steps: 1 (Joy) -> 3 (Excited) -> 1 (Energetic) -> 8 -> 'c' -> 'q'
        inputs = ["1", "3", "1", "8", "c", "q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
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
        self.assertIn("Generate 10 songs based on the following mood profile.", prompt)

    def test_import_songs_and_create_playlist(self):
        json_songs = '{"songs": [{"title": "September", "artist": "Earth, Wind & Fire"}]}'
        # Steps: 1 (Joy) -> 3 (Excited) -> 1 (Energetic) -> 8 -> 'c' -> 'i' (import) -> paste songs -> blank line
        inputs = ["1", "3", "1", "8", "c", "i", json_songs, ""]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()
        self.assertIsNotNone(result)
        self.assertTrue(any("SPOTIFY PLAYLIST CREATED" in out for out in helper.outputs))
        self.assertEqual(len(self.mock_http.created_playlists), 1)
        self.assertTrue(self.mock_http.created_playlists[0]["name"].startswith("Joy — Excited — Energetic — "))

    def test_custom_song_count_in_cli(self):
        custom_config = AppConfig(song_count=20, output_format="json")
        inputs = ["1", "3", "1", "8", "c", "q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=custom_config,
            spotify_client=self.spotify_client,
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
            "c", "q"
        ]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
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
        inputs = ["2", "b", "1", "3", "b", "1", "2", "5", "c", "q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
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
        inputs = ["1", "3", "1", "8", "r", "3", "1", "2", "6", "c", "q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
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
        inputs = ["1", "3", "1", "8", "e", "4", "10", "c", "q"]
        helper = MockCLIHelper(inputs)

        cli = MoodSelectionCLI(
            taxonomy=self.taxonomy,
            config=self.config,
            spotify_client=self.spotify_client,
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
            spotify_client=self.spotify_client,
            input_func=helper.mock_input,
            output_func=helper.mock_print,
        )
        result = cli.run()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
