"""Unit tests for application configuration loading and validation."""

import json
import tempfile
import unittest
from pathlib import Path

from src.config import AppConfig, ConfigError, load_config, validate_config


class TestAppConfig(unittest.TestCase):
    """Test suite for application configuration."""

    def test_load_default_config(self):
        config = load_config()
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.song_count, 10)

    def test_load_custom_config_file(self):
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            json.dump({"song_count": 25}, f)
            temp_path = f.name

        try:
            config = load_config(temp_path)
            self.assertEqual(config.song_count, 25)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_validate_valid_config(self):
        config = validate_config({"song_count": 15})
        self.assertEqual(config.song_count, 15)

    def test_validate_missing_song_count(self):
        with self.assertRaises(ConfigError) as ctx:
            validate_config({})
        self.assertIn("Missing required configuration field: 'song_count'", str(ctx.exception))

    def test_validate_non_integer_song_count(self):
        for invalid_val in ["10", 10.5, True, False, None, [10]]:
            with self.assertRaises(ConfigError):
                validate_config({"song_count": invalid_val})

    def test_validate_zero_or_negative_song_count(self):
        for invalid_val in [0, -1, -100]:
            with self.assertRaises(ConfigError) as ctx:
                validate_config({"song_count": invalid_val})
            self.assertIn("must be a positive integer", str(ctx.exception))

    def test_load_nonexistent_file(self):
        with self.assertRaises(ConfigError) as ctx:
            load_config("nonexistent_config_file_12345.json")
        self.assertIn("Configuration file not found", str(ctx.exception))

    def test_load_malformed_json_file(self):
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
            f.write("{ invalid_json: true ")
            temp_path = f.name

        try:
            with self.assertRaises(ConfigError) as ctx:
                load_config(temp_path)
            self.assertIn("Malformed JSON", str(ctx.exception))
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
