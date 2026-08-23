"""Unit tests for Spotify integration, environment variable credentials, token refresh, and playlist creation."""

import base64
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from src.models import MoodProfile, ResolvedTrack, SongRecommendation
from src.spotify import (
    DEFAULT_REDIRECT_URI,
    SpotifyAuthError,
    SpotifyClient,
    SpotifyError,
    extract_code_from_input,
)


class MockSpotifyHTTPRequester:
    """Mock HTTP requester simulating Spotify Web API endpoints."""

    def __init__(self):
        self.search_db: Dict[str, Dict[str, Any]] = {
            "september": {
                "tracks": {
                    "items": [
                        {
                            "name": "September",
                            "artists": [{"name": "Earth, Wind & Fire"}],
                            "uri": "spotify:track:september123",
                            "id": "september123",
                            "external_urls": {"spotify": "https://open.spotify.com/track/september123"},
                            "album": {"name": "The Best of Earth, Wind & Fire"},
                        }
                    ]
                }
            },
            "weightless": {
                "tracks": {
                    "items": [
                        {
                            "name": "Weightless",
                            "artists": [{"name": "Marconi Union"}],
                            "uri": "spotify:track:weightless456",
                            "id": "weightless456",
                            "external_urls": {"spotify": "https://open.spotify.com/track/weightless456"},
                            "album": {"name": "Weightless (Ambient Transmissions Vol. 2)"},
                        }
                    ]
                }
            },
        }
        self.created_playlists: List[Dict[str, Any]] = []
        self.added_tracks: List[Dict[str, Any]] = []
        self.last_token_request: Optional[Dict[str, Any]] = None

    def __call__(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if "api/token" in url:
            self.last_token_request = {"headers": headers, "data": data}
            return {
                "access_token": "mock_generated_access_token_789",
                "refresh_token": "mock_refresh_token_789",
                "expires_in": 3600,
            }

        if "/search" in url:
            for key, val in self.search_db.items():
                if key in url.lower():
                    return val
            return {"tracks": {"items": []}}

        if "/me" in url and method == "GET":
            return {"id": "test_user_123", "display_name": "Test User"}

        if "/playlists" in url and method == "POST":
            if "/items" in url or "/tracks" in url:
                self.added_tracks.append({"url": url, "data": data})
                return {"snapshot_id": "snapshot_123"}
            else:
                playlist_id = f"playlist_{len(self.created_playlists) + 1}"
                payload = data if isinstance(data, dict) else {}
                result = {
                    "id": playlist_id,
                    "name": payload.get("name", "Test Playlist"),
                    "external_urls": {"spotify": f"https://open.spotify.com/playlist/{playlist_id}"},
                }
                self.created_playlists.append(result)
                return result

        return {}


class TestSpotifyIntegration(unittest.TestCase):
    """Test suite for Spotify track resolution, environment credentials, token handling, and playlist creation."""

    def setUp(self):
        self.mock_http = MockSpotifyHTTPRequester()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_cache = Path(self.temp_dir.name) / "test_cache.json"
        self.client = SpotifyClient(
            access_token="test_valid_access_token",
            token_cache_path=self.temp_cache,
            http_requester=self.mock_http,
        )
        self.profile = MoodProfile(
            intensity=1,
            core_emotion="Joy",
            branch="Content",
            specific_emotion="Peaceful",
            code="J-1-1:1",
            intensity_label="Crisis / Exhausted",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_code_from_input(self):
        url1 = "http://127.0.0.1:8888/callback?code=AQD123_abc"
        self.assertEqual(extract_code_from_input(url1), "AQD123_abc")

        url2 = "http://127.0.0.1:8888/callback?code=AQD123_abc#_=_"
        self.assertEqual(extract_code_from_input(url2), "AQD123_abc")

        raw_code = "  AQD123_raw#_=_  "
        self.assertEqual(extract_code_from_input(raw_code), "AQD123_raw")

    def test_missing_credentials_raises_auth_error(self):
        with patch.dict(os.environ, {}, clear=True):
            empty_client = SpotifyClient(
                client_id="",
                client_secret="",
                access_token="",
                token_cache_path=self.temp_cache,
            )
            with self.assertRaises(SpotifyAuthError) as ctx:
                empty_client.authenticate()
            self.assertIn("Spotify credentials not found", str(ctx.exception))

    def test_credentials_read_from_environment_variables(self):
        env_vars = {
            "SPOTIFY_CLIENT_ID": "env_test_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_test_client_secret",
            "SPOTIFY_REDIRECT_URI": "http://localhost:9999/callback",
            "SPOTIFY_ACCESS_TOKEN": "env_test_token",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            client = SpotifyClient(token_cache_path=self.temp_cache)
            self.assertEqual(client.client_id, "env_test_client_id")
            self.assertEqual(client.client_secret, "env_test_client_secret")
            self.assertEqual(client.redirect_uri, "http://localhost:9999/callback")
            self.assertEqual(client.access_token, "env_test_token")

    def test_redirect_uri_defaults_when_env_not_set(self):
        env_vars = {
            "SPOTIFY_CLIENT_ID": "env_test_client_id",
            "SPOTIFY_CLIENT_SECRET": "env_test_client_secret",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            client = SpotifyClient(token_cache_path=self.temp_cache)
            self.assertEqual(client.redirect_uri, DEFAULT_REDIRECT_URI)

    def test_access_token_env_var_validates_user_profile(self):
        env_vars = {"SPOTIFY_ACCESS_TOKEN": "direct_env_token_abc"}
        with patch.dict(os.environ, env_vars, clear=True):
            client = SpotifyClient(
                token_cache_path=self.temp_cache,
                http_requester=self.mock_http,
            )
            client.authenticate()
            self.assertEqual(client.access_token, "direct_env_token_abc")
            self.assertEqual(client.get_current_user_id(), "test_user_123")

    def test_oauth_token_exchange_and_user_profile(self):
        env_vars = {
            "SPOTIFY_CLIENT_ID": "test_id_123",
            "SPOTIFY_CLIENT_SECRET": "test_secret_456",
            "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
        }
        outputs = []
        with patch.dict(os.environ, env_vars, clear=True):
            client = SpotifyClient(
                token_cache_path=self.temp_cache,
                http_requester=self.mock_http,
                input_func=lambda prompt: "http://127.0.0.1:8888/callback?code=mock_code_xyz",
                output_func=lambda msg: outputs.append(msg),
            )
            client.authenticate()
            self.assertEqual(client.access_token, "mock_generated_access_token_789")
            self.assertIsNotNone(self.mock_http.last_token_request)

            # Verify Basic auth header in token request matches client_id:client_secret
            expected_basic = base64.b64encode("test_id_123:test_secret_456".encode()).decode()
            auth_header = self.mock_http.last_token_request["headers"].get("Authorization")
            self.assertEqual(auth_header, f"Basic {expected_basic}")

            # Verify user diagnostic output
            self.assertTrue(any("Test User" in m for m in outputs))
            self.assertTrue(any("test_user_123" in m for m in outputs))

    def test_search_track_found(self):
        track = self.client.search_track("September", "Earth, Wind & Fire")
        self.assertIsNotNone(track)
        self.assertEqual(track.title, "September")
        self.assertEqual(track.artist, "Earth, Wind & Fire")
        self.assertEqual(track.spotify_uri, "spotify:track:september123")

    def test_search_track_not_found(self):
        track = self.client.search_track("Nonexistent Song", "Unknown Artist")
        self.assertIsNone(track)

    def test_resolve_songs_partial_success(self):
        recs = [
            SongRecommendation(title="September", artist="Earth, Wind & Fire"),
            SongRecommendation(title="Unknown Fictional Song", artist="Nobody"),
            SongRecommendation(title="Weightless", artist="Marconi Union"),
        ]
        resolved, unresolved = self.client.resolve_songs(recs)

        self.assertEqual(len(resolved), 2)
        self.assertEqual(len(unresolved), 1)

        self.assertEqual(resolved[0].title, "September")
        self.assertEqual(resolved[1].title, "Weightless")
        self.assertEqual(unresolved[0].title, "Unknown Fictional Song")
        self.assertIn("No match found on Spotify", unresolved[0].reason)

    def test_create_playlist_success(self):
        tracks = [
            ResolvedTrack(
                title="September",
                artist="Earth, Wind & Fire",
                spotify_uri="spotify:track:september123",
                spotify_id="september123",
            ),
            ResolvedTrack(
                title="Weightless",
                artist="Marconi Union",
                spotify_uri="spotify:track:weightless456",
                spotify_id="weightless456",
            ),
        ]

        result = self.client.create_playlist(profile=self.profile, tracks=tracks)

        self.assertTrue(result.playlist_name.startswith("Joy — Content — Peaceful — "))
        self.assertEqual(result.playlist_id, "playlist_1")
        self.assertEqual(result.success_count, 2)
        self.assertEqual(result.total_recommendations, 2)
        self.assertEqual(result.playlist_url, "https://open.spotify.com/playlist/playlist_1")

        # Verify tracks were added to mock
        self.assertEqual(len(self.mock_http.added_tracks), 1)
        self.assertEqual(
            self.mock_http.added_tracks[0]["data"]["uris"],
            ["spotify:track:september123", "spotify:track:weightless456"],
        )

    def test_format_playlist_name_with_timestamp(self):
        dt = datetime(2026, 8, 23, 15, 42)
        formatted_name = self.profile.format_playlist_name(timestamp=dt)
        self.assertEqual(formatted_name, "Joy — Content — Peaceful — Aug 23, 2026 3:42 PM")

    def test_create_playlist_with_zero_tracks_raises_error(self):
        with self.assertRaises(SpotifyError):
            self.client.create_playlist(profile=self.profile, tracks=[])


if __name__ == "__main__":
    unittest.main()
