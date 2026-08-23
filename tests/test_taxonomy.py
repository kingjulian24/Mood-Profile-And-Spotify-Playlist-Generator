"""Tests for MoodTaxonomy loading, traversal, and profile/code construction."""

import unittest
from pathlib import Path

from src.taxonomy import MoodTaxonomy
from src.models import MoodProfile


class TestMoodTaxonomy(unittest.TestCase):
    """Test suite for the canonical taxonomy loader and validator."""

    def setUp(self):
        self.taxonomy = MoodTaxonomy()

    def test_taxonomy_loads_all_six_core_emotions(self):
        core_emotions = self.taxonomy.core_emotions
        expected = ["Joy", "Sadness", "Anger", "Fear", "Disgust", "Surprise"]
        self.assertEqual(core_emotions, expected)

    def test_core_emotion_lookup_by_index_and_name(self):
        core_by_name = self.taxonomy.get_core_emotion("Joy")
        self.assertEqual(core_by_name.name, "Joy")
        self.assertEqual(core_by_name.code_letter, "J")

        core_by_index = self.taxonomy.get_core_emotion(1)
        self.assertEqual(core_by_index.name, "Joy")

        with self.assertRaises(IndexError):
            self.taxonomy.get_core_emotion(0)

        with self.assertRaises(IndexError):
            self.taxonomy.get_core_emotion(7)

        with self.assertRaises(KeyError):
            self.taxonomy.get_core_emotion("NonExistentEmotion")

    def test_branch_lookup_and_traversal(self):
        joy_branches = self.taxonomy.get_branches("Joy")
        self.assertEqual(joy_branches, ["Content", "Happy", "Excited"])

        branch_3 = self.taxonomy.get_branch("Joy", 3)
        self.assertEqual(branch_3.name, "Excited")

        with self.assertRaises(IndexError):
            self.taxonomy.get_branch("Joy", 4)
        with self.assertRaises(KeyError):
            self.taxonomy.get_branch("Joy", "InvalidBranch")

    def test_specific_emotion_lookup_and_traversal(self):
        specifics = self.taxonomy.get_specific_emotions("Joy", "Excited")
        self.assertEqual(specifics, ["Energetic", "Enthusiastic"])

        specific_1 = self.taxonomy.get_specific_emotion("Joy", "Excited", 1)
        self.assertEqual(specific_1, "Energetic")

        with self.assertRaises(IndexError):
            self.taxonomy.get_specific_emotion("Joy", "Excited", 3)

        with self.assertRaises(KeyError):
            self.taxonomy.get_specific_emotion("Joy", "Excited", "InvalidSpecific")

    def test_intensity_validation_and_labels(self):
        label, desc = self.taxonomy.get_intensity_info(1)
        self.assertEqual(label, "Crisis / Exhausted")

        label, desc = self.taxonomy.get_intensity_info(8)
        self.assertEqual(label, "Positive / Stable")

        label, desc = self.taxonomy.get_intensity_info(10)
        self.assertEqual(label, "Peak State")

        with self.assertRaises(ValueError):
            self.taxonomy.get_intensity_info(0)
        with self.assertRaises(ValueError):
            self.taxonomy.get_intensity_info(11)
        with self.assertRaises(ValueError):
            self.taxonomy.get_intensity_info(-5)

    def test_build_mood_profile_valid(self):
        profile = self.taxonomy.build_mood_profile(
            core_index=1,
            branch_index=3,
            specific_index=1,
            intensity=8,
        )
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Excited")
        self.assertEqual(profile.specific_emotion, "Energetic")
        self.assertEqual(profile.intensity, 8)
        self.assertEqual(profile.code, "J-3-1:8")
        self.assertEqual(profile.intensity_label, "Positive / Stable")

        d = profile.to_dict()
        self.assertEqual(d["code"], "J-3-1:8")
        self.assertEqual(d["core_emotion"], "Joy")
        self.assertEqual(d["intensity"], 8)
        self.assertEqual(d["taxonomy_path"]["branch"], "Excited")

    def test_build_from_names_valid(self):
        profile = self.taxonomy.build_from_names(
            core_emotion="Joy",
            branch="Excited",
            specific_emotion="Energetic",
            intensity=8,
        )
        self.assertEqual(profile.code, "J-3-1:8")
        self.assertEqual(profile.core_index, 1)
        self.assertEqual(profile.branch_index, 3)
        self.assertEqual(profile.specific_index, 1)

    def test_parse_mood_code(self):
        profile = self.taxonomy.parse_code("J-3-1:8")
        self.assertEqual(profile.core_emotion, "Joy")
        self.assertEqual(profile.branch, "Excited")
        self.assertEqual(profile.specific_emotion, "Energetic")
        self.assertEqual(profile.intensity, 8)
        self.assertEqual(profile.code, "J-3-1:8")

        profile_sad = self.taxonomy.parse_code("S-3-1:4")
        self.assertEqual(profile_sad.core_emotion, "Sadness")
        self.assertEqual(profile_sad.branch, "Sluggish")
        self.assertEqual(profile_sad.specific_emotion, "Heavy")
        self.assertEqual(profile_sad.intensity, 4)

    def test_parse_invalid_mood_code(self):
        with self.assertRaises(ValueError):
            self.taxonomy.parse_code("InvalidCode")

        with self.assertRaises(ValueError):
            self.taxonomy.parse_code("J-3-1")

        with self.assertRaises(ValueError):
            self.taxonomy.parse_code("Z-1-1:5")

        with self.assertRaises(IndexError):
            self.taxonomy.parse_code("J-9-1:5")

        with self.assertRaises(ValueError):
            self.taxonomy.parse_code("J-1-1:15")


if __name__ == "__main__":
    unittest.main()
