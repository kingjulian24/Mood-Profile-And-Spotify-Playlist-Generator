"""Unit tests for machine-readable song recommendation output parsers."""

import unittest
from src.models import SongRecommendation
from src.song_parser import SongParseError, parse_song_list


class TestSongParser(unittest.TestCase):
    """Test suite for parsing chatbot song recommendation outputs."""

    def test_parse_valid_json_object(self):
        json_input = """
        {
          "songs": [
            {"title": "Weightless", "artist": "Marconi Union"},
            {"title": "Clair de Lune", "artist": "Claude Debussy"}
          ]
        }
        """
        songs = parse_song_list(json_input, format_hint="json")
        self.assertEqual(len(songs), 2)
        self.assertEqual(songs[0].title, "Weightless")
        self.assertEqual(songs[0].artist, "Marconi Union")
        self.assertEqual(songs[1].title, "Clair de Lune")
        self.assertEqual(songs[1].artist, "Claude Debussy")

    def test_parse_valid_json_array(self):
        json_input = """
        [
          {"title": "Electric Feel", "artist": "MGMT"},
          {"title": "Midnight City", "artist": "M83"}
        ]
        """
        songs = parse_song_list(json_input)
        self.assertEqual(len(songs), 2)
        self.assertEqual(songs[0].title, "Electric Feel")
        self.assertEqual(songs[0].artist, "MGMT")

    def test_parse_json_with_markdown_fences(self):
        fenced = """```json
        {
          "songs": [
            {"title": "September", "artist": "Earth, Wind & Fire"}
          ]
        }
        ```"""
        songs = parse_song_list(fenced)
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, "September")
        self.assertEqual(songs[0].artist, "Earth, Wind & Fire")

    def test_parse_valid_csv(self):
        csv_input = """title,artist
        Weightless,Marconi Union
        "Clair de Lune",Claude Debussy
        "Walking on Sunshine","Katrina and the Waves"
        """
        songs = parse_song_list(csv_input, format_hint="csv")
        self.assertEqual(len(songs), 3)
        self.assertEqual(songs[0].title, "Weightless")
        self.assertEqual(songs[0].artist, "Marconi Union")
        self.assertEqual(songs[1].title, "Clair de Lune")
        self.assertEqual(songs[2].title, "Walking on Sunshine")
        self.assertEqual(songs[2].artist, "Katrina and the Waves")

    def test_parse_csv_with_markdown_fences(self):
        fenced_csv = """```csv
title,artist
Happy,Pharrell Williams
```"""
        songs = parse_song_list(fenced_csv)
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, "Happy")
        self.assertEqual(songs[0].artist, "Pharrell Williams")

    def test_parse_valid_yaml(self):
        yaml_input = """
        songs:
          - title: "Feeling Good"
            artist: "Nina Simone"
          - title: "Here Comes the Sun"
            artist: "The Beatles"
        """
        songs = parse_song_list(yaml_input, format_hint="yaml")
        self.assertEqual(len(songs), 2)
        self.assertEqual(songs[0].title, "Feeling Good")
        self.assertEqual(songs[0].artist, "Nina Simone")
        self.assertEqual(songs[1].title, "Here Comes the Sun")
        self.assertEqual(songs[1].artist, "The Beatles")

    def test_parse_yaml_with_markdown_fences(self):
        fenced_yaml = """```yaml
songs:
  - title: "Heroes"
    artist: "David Bowie"
```"""
        songs = parse_song_list(fenced_yaml)
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].title, "Heroes")
        self.assertEqual(songs[0].artist, "David Bowie")

    def test_empty_input_raises_error(self):
        with self.assertRaises(SongParseError):
            parse_song_list("")

    def test_invalid_json_missing_fields_raises_error(self):
        bad_json = '{"songs": [{"title": "Only Title"}]}'
        with self.assertRaises(SongParseError) as ctx:
            parse_song_list(bad_json, format_hint="json")
        self.assertIn("missing a valid 'artist' field", str(ctx.exception))

    def test_empty_json_songs_list_raises_error(self):
        empty_json = '{"songs": []}'
        with self.assertRaises(SongParseError):
            parse_song_list(empty_json, format_hint="json")

    def test_malformed_csv_raises_error(self):
        bad_csv = "genre,duration\nPop,3:45"
        with self.assertRaises(SongParseError):
            parse_song_list(bad_csv, format_hint="csv")


if __name__ == "__main__":
    unittest.main()
