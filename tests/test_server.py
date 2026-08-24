"""Unit tests for the Python backend REST API server handler using mock streams."""

import io
import json
import unittest
from http import HTTPStatus
from unittest.mock import patch

from src.server import APIServerHandler


class MockSocket:
    """Mock socket for testing BaseHTTPRequestHandler without TCP binding."""

    def __init__(self, request_bytes: bytes):
        self.rfile = io.BytesIO(request_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode: str, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, data: bytes):
        self.wfile.write(data)

    def send(self, data: bytes):
        self.wfile.write(data)
        return len(data)


def execute_request(method: str, path: str, body: dict = None, headers: dict = None) -> tuple[int, dict]:
    """Execute a request against APIServerHandler using in-memory streams."""
    headers_dict = headers or {}
    body_bytes = b""
    if body is not None:
        body_bytes = json.dumps(body).encode("utf-8")
        headers_dict["Content-Type"] = "application/json"
        headers_dict["Content-Length"] = str(len(body_bytes))

    header_lines = [f"{method} {path} HTTP/1.1", "Host: localhost"]
    for k, v in headers_dict.items():
        header_lines.append(f"{k}: {v}")
    raw_request = "\r\n".join(header_lines).encode("utf-8") + b"\r\n\r\n" + body_bytes

    sock = MockSocket(raw_request)
    with patch.object(APIServerHandler, "log_message"):
        handler = APIServerHandler(sock, ("127.0.0.1", 12345), None)

    response_data = sock.wfile.getvalue()
    header_end = response_data.find(b"\r\n\r\n")
    if header_end == -1:
        return 500, {}

    header_part = response_data[:header_end].decode("utf-8")
    body_part = response_data[header_end + 4:].decode("utf-8")

    status_line = header_part.splitlines()[0]
    status_code = int(status_line.split()[1])

    json_body = json.loads(body_part) if body_part else {}
    return status_code, json_body


class TestAPIServerHandler(unittest.TestCase):
    """Test suite for HTTP REST API server endpoints without network binding."""

    def test_health_endpoint(self):
        status, data = execute_request("GET", "/api/health")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "0.1.0")

    def test_config_endpoint(self):
        status, data = execute_request("GET", "/api/config")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("song_count", data)
        self.assertIn("output_format", data)

    def test_taxonomy_endpoint(self):
        status, data = execute_request("GET", "/api/taxonomy")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("core_emotions", data)
        self.assertIn("intensity_levels", data)
        self.assertEqual(len(data["core_emotions"]), 6)

    def test_profile_generation_from_names(self):
        status, data = execute_request("POST", "/api/profile", body={
            "core_emotion": "Joy",
            "branch": "Excited",
            "specific_emotion": "Energetic",
            "intensity": 8,
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data["code"], "J-3-1:8")
        self.assertEqual(data["specific_emotion"], "Energetic")

    def test_profile_generation_from_code(self):
        status, data = execute_request("POST", "/api/profile", body={"code": "A-1-2:6"})
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data["core_emotion"], "Anger")
        self.assertEqual(data["branch"], "Irritated")
        self.assertEqual(data["specific_emotion"], "Frustrated")
        self.assertEqual(data["intensity"], 6)

    def test_prompt_generation_endpoint(self):
        status, data = execute_request("POST", "/api/prompt", body={
            "profile": {
                "core_emotion": "Joy",
                "branch": "Content",
                "specific_emotion": "Peaceful",
                "code": "J-1-1:1",
                "intensity": 1,
            },
            "song_count": 5,
            "output_format": "json",
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertIn("Generate 5 songs", data["prompt"])
        self.assertIn("J-1-1:1", data["prompt"])

    def test_song_parse_endpoint(self):
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": '{"songs": [{"title": "September", "artist": "Earth, Wind & Fire"}]}',
            "format_hint": "json",
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["valid"])
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["songs"][0]["title"], "September")

    def test_song_parse_csv_and_yaml(self):
        # CSV format
        csv_text = "title,artist\n\"Levitating\",\"Dua Lipa\"\n\"24K Magic\",\"Bruno Mars\""
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": csv_text,
            "format_hint": "csv",
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["valid"])
        self.assertEqual(data["count"], 2)

        # YAML format
        yaml_text = "songs:\n  - title: \"Golden\"\n    artist: \"Jill Scott\""
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": yaml_text,
            "format_hint": "yaml",
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertTrue(data["valid"])
        self.assertEqual(data["count"], 1)

    def test_song_parse_empty_response(self):
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": "   ",
        })
        self.assertEqual(status, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(data["valid"])
        self.assertIn("empty", data["error"].lower())

    def test_song_parse_invalid_json(self):
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": "{ invalid json",
            "format_hint": "json",
        })
        self.assertEqual(status, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(data["valid"])
        self.assertIn("JSON", data["error"])

    def test_song_parse_missing_artist_or_title(self):
        status, data = execute_request("POST", "/api/songs/parse", body={
            "raw_text": '{"songs": [{"title": "Only Title"}]}',
            "format_hint": "json",
        })
        self.assertEqual(status, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertFalse(data["valid"])
        self.assertIn("artist", data["error"].lower())

    @patch("src.server.SpotifyClient")
    def test_spotify_resolve_endpoint(self, mock_spotify_cls):
        from src.models import ResolvedTrack, UnresolvedTrack
        mock_client = mock_spotify_cls.return_value
        mock_client.resolve_songs.return_value = (
            [ResolvedTrack(title="September", artist="Earth, Wind & Fire", spotify_uri="spotify:track:123", spotify_id="123", spotify_url="http://spotify/123", album_name="Album")],
            [UnresolvedTrack(title="Unknown", artist="Nobody", reason="No match found on Spotify")],
        )

        status, data = execute_request("POST", "/api/spotify/resolve", body={
            "songs": [
                {"title": "September", "artist": "Earth, Wind & Fire"},
                {"title": "Unknown", "artist": "Nobody"},
            ]
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data["resolved_count"], 1)
        self.assertEqual(len(data["resolved"]), 1)
        self.assertEqual(len(data["unresolved"]), 1)

    @patch("src.server.SpotifyClient")
    def test_spotify_playlist_create_endpoint(self, mock_spotify_cls):
        from src.models import PlaylistResult, ResolvedTrack
        mock_client = mock_spotify_cls.return_value
        mock_track = ResolvedTrack(
            title="September",
            artist="Earth, Wind & Fire",
            spotify_uri="spotify:track:123",
            spotify_id="123",
        )
        mock_client.create_playlist.return_value = PlaylistResult(
            playlist_id="playlist_abc",
            playlist_name="Joy — Excited — Energetic — Aug 24, 2026 12:00 AM",
            playlist_url="https://open.spotify.com/playlist/playlist_abc",
            resolved_tracks=[mock_track],
        )

        status, data = execute_request("POST", "/api/spotify/playlist", body={
            "profile": {
                "core_emotion": "Joy",
                "branch": "Excited",
                "specific_emotion": "Energetic",
                "code": "J-3-1:8",
                "intensity": 8,
            },
            "tracks": [
                {
                    "title": "September",
                    "artist": "Earth, Wind & Fire",
                    "spotify_uri": "spotify:track:123",
                    "spotify_id": "123",
                }
            ]
        })
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(data["playlist_id"], "playlist_abc")
        self.assertEqual(data["tracks_added"], 1)


if __name__ == "__main__":
    unittest.main()
