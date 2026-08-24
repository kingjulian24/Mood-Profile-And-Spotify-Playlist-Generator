"""Security test suite validating credential protection, OAuth state validation,
body size limits, safe parsing, and token cache permissions."""

import io
import json
import os
import stat
import tempfile
import time
import unittest
from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.models import SongRecommendation
from src.server import APIServerHandler, OAuthCallbackHandler, _PENDING_OAUTH_STATES, _OAUTH_STATE_LOCK
from src.song_parser import parse_song_list, SongParseError
from src.spotify import SpotifyClient, SpotifyAuthError


def execute_server_request(method: str, path: str, body: dict = None, headers: dict = None):
    """Helper to simulate an HTTP request to APIServerHandler without live networking."""
    req_body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""
    req_headers = {
        "Content-Length": str(len(req_body_bytes)),
        "Content-Type": "application/json",
    }
    if headers:
        req_headers.update(headers)

    class FakeSocket:
        def __init__(self, data):
            self._rfile = io.BytesIO(data)
            self._wfile = io.BytesIO()

        def makefile(self, mode, *args, **kwargs):
            if "r" in mode:
                return self._rfile
            return self._wfile

    socket = FakeSocket(req_body_bytes)

    with patch.object(APIServerHandler, "setup"), \
         patch.object(APIServerHandler, "finish"):
        handler = APIServerHandler.__new__(APIServerHandler)
        handler.rfile = socket.makefile("rb")
        handler.wfile = socket.makefile("wb")
        handler.headers = req_headers
        handler.command = method
        handler.path = path
        handler.requestline = f"{method} {path} HTTP/1.0"
        handler.request_version = "HTTP/1.0"
        handler.server_version = "BaseHTTP/0.6"
        handler.sys_version = "Python/3.x"
        handler.protocol_version = "HTTP/1.0"
        handler.close_connection = True

        if method == "GET":
            handler.do_GET()
        elif method == "POST":
            handler.do_POST()

        raw_output = handler.wfile.getvalue().decode("utf-8", errors="replace")
        lines = raw_output.split("\r\n")
        status_line = lines[0] if lines else ""
        status_code = int(status_line.split()[1]) if len(status_line.split()) > 1 else 500

        body_start = raw_output.find("\r\n\r\n")
        response_body = raw_output[body_start + 4:] if body_start != -1 else ""
        parsed_json = {}
        if response_body:
            try:
                parsed_json = json.loads(response_body)
            except Exception:
                pass

        return status_code, parsed_json


class TestSecurity(unittest.TestCase):
    """Security verification tests."""

    def test_config_never_exposes_secrets(self):
        """Verify /api/config only returns safe application settings."""
        with patch.dict(os.environ, {
            "SPOTIFY_CLIENT_ID": "super_secret_client_id",
            "SPOTIFY_CLIENT_SECRET": "super_secret_client_secret",
            "SPOTIFY_ACCESS_TOKEN": "secret_access_token_val",
        }):
            status, data = execute_server_request("GET", "/api/config")
            self.assertEqual(status, HTTPStatus.OK)
            # Must only expose song_count and output_format
            self.assertIn("song_count", data)
            self.assertIn("output_format", data)
            self.assertNotIn("client_secret", data)
            self.assertNotIn("super_secret_client_secret", str(data))
            self.assertNotIn("secret_access_token_val", str(data))

    def test_spotify_status_never_exposes_tokens(self):
        """Verify /api/spotify/status never exposes access/refresh tokens or client secrets."""
        with patch("src.server.SpotifyClient") as mock_cls:
            mock_inst = mock_cls.return_value
            mock_inst.validate_cached_token.return_value = True
            mock_inst.access_token = "exposed_bearer_token_12345"
            mock_inst.refresh_token = "exposed_refresh_token_67890"
            mock_inst.client_secret = "exposed_secret_9999"
            mock_inst.user_profile = {"id": "user_id_val", "display_name": "Test User"}

            status, data = execute_server_request("GET", "/api/spotify/status")
            self.assertEqual(status, HTTPStatus.OK)
            self.assertTrue(data["authenticated"])
            self.assertNotIn("exposed_bearer_token_12345", str(data))
            self.assertNotIn("exposed_refresh_token_67890", str(data))
            self.assertNotIn("exposed_secret_9999", str(data))
            self.assertNotIn("token", data)

    def test_token_cache_permissions_are_owner_only(self):
        """Verify that SpotifyClient saves token cache files with strict 0600 permissions."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            client = SpotifyClient(
                client_id="test_id",
                client_secret="test_secret",
                token_cache_path=tmp_path,
            )
            client._save_cached_token({"access_token": "secret_tok", "refresh_token": "ref_tok"})

            # Check file permissions mode on POSIX systems
            file_stat = os.stat(tmp_path)
            mode = stat.S_IMODE(file_stat.st_mode)
            # Owner read/write (0o600)
            self.assertEqual(mode, 0o600)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_oversized_payload_rejection(self):
        """Verify server rejects oversized request payloads exceeding max limit."""
        oversized_text = "a" * (APIServerHandler.MAX_REQUEST_BODY_SIZE + 100)
        status, data = execute_server_request("POST", "/api/songs/parse", headers={
            "Content-Length": str(len(oversized_text)),
        })
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertIn("exceeds maximum", data.get("error", ""))

    def test_oauth_state_generation_and_validation(self):
        """Verify OAuth state generation and CSRF protection in callback handler."""
        with patch("src.server.SpotifyClient") as mock_cls:
            mock_inst = mock_cls.return_value
            mock_inst.get_authorize_url.side_effect = lambda state=None: f"https://accounts.spotify.com/authorize?state={state}"
            mock_inst.redirect_uri = "http://127.0.0.1:8888/callback"

            # 1. Start auth -> creates valid state
            status, data = execute_server_request("GET", "/api/spotify/auth/start")
            self.assertEqual(status, HTTPStatus.OK)
            auth_url = data["auth_url"]
            self.assertIn("state=", auth_url)

            # Extract generated state
            state_val = auth_url.split("state=")[1]
            self.assertTrue(len(state_val) >= 20)

            # Verify state exists in pending states
            with _OAUTH_STATE_LOCK:
                self.assertIn(state_val, _PENDING_OAUTH_STATES)

    def test_oauth_callback_rejects_missing_or_invalid_state(self):
        """Verify OAuthCallbackHandler rejects requests without valid state."""
        class FakeCallbackSocket:
            def __init__(self):
                self._wfile = io.BytesIO()

            def makefile(self, mode, *args, **kwargs):
                return self._wfile

        def simulate_callback(query_string: str):
            socket = FakeCallbackSocket()
            with patch.object(OAuthCallbackHandler, "setup"), \
                 patch.object(OAuthCallbackHandler, "finish"):
                handler = OAuthCallbackHandler.__new__(OAuthCallbackHandler)
                handler.wfile = socket._wfile
                handler.rfile = io.BytesIO()
                handler.headers = {}
                handler.command = "GET"
                handler.path = f"/callback?{query_string}"
                handler.requestline = f"GET /callback?{query_string} HTTP/1.0"
                handler.request_version = "HTTP/1.0"
                handler.server_version = "BaseHTTP/0.6"
                handler.sys_version = "Python/3.x"
                handler.protocol_version = "HTTP/1.0"
                handler.close_connection = True
                handler.do_GET()

                output = handler.wfile.getvalue().decode("utf-8", errors="replace")
                return output

        # 1. Missing state -> rejected
        out_missing = simulate_callback("code=valid_code")
        self.assertIn("400 Bad Request", out_missing)
        self.assertIn("Invalid or Expired OAuth Session", out_missing)

        # 2. Invalid state -> rejected
        out_invalid = simulate_callback("code=valid_code&state=fake_nonexistent_state")
        self.assertIn("400 Bad Request", out_invalid)
        self.assertIn("Invalid or Expired OAuth Session", out_invalid)

        # 3. Valid state -> accepted and single-use
        test_state = "valid_test_security_state_999"
        with _OAUTH_STATE_LOCK:
            _PENDING_OAUTH_STATES[test_state] = time.time()

        with patch("src.server.SpotifyClient") as mock_cls:
            mock_inst = mock_cls.return_value
            mock_inst.exchange_code_for_token.return_value = {"id": "user1", "display_name": "User One"}
            out_valid = simulate_callback(f"code=valid_code&state={test_state}")
            self.assertIn("200 OK", out_valid)
            self.assertIn("Spotify Connected!", out_valid)

        # Re-using the same state should now fail (single-use check)
        out_replay = simulate_callback(f"code=valid_code&state={test_state}")
        self.assertIn("400 Bad Request", out_replay)

    def test_chatbot_untrusted_input_safety(self):
        """Verify that malformed and hostile chatbot inputs cannot execute code or crash parser."""
        hostile_inputs = [
            # Hostile prototype pollution / dict injection strings
            '{"__proto__": {"admin": true}, "songs": [{"title": "Song1", "artist": "Artist1"}]}',
            # Shell metacharacters and SQL-like strings
            'title,artist\n"$(rm -rf /) ; DROP TABLE users; --","Artist \'; echo pwned"',
            # HTML/Script tag strings
            'songs:\n  - title: "<script>alert(1)</script>"\n    artist: "<img src=x onerror=alert(2)>"',
        ]

        for hostile in hostile_inputs:
            songs = parse_song_list(hostile)
            self.assertTrue(len(songs) >= 1)
            for s in songs:
                self.assertIsInstance(s.title, str)
                self.assertIsInstance(s.artist, str)


if __name__ == "__main__":
    unittest.main()
