"""HTTP API server providing backend services for the React GUI presentation layer."""

from __future__ import annotations
import json
import os
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from src.config import ConfigError, load_config
from src.models import MoodProfile, PlaylistResult, ResolvedTrack, SongRecommendation, UnresolvedTrack
from src.prompt import generate_recommendation_prompt
from src.song_parser import SongParseError, parse_song_list
from src.spotify import SpotifyClient, SpotifyError
from src.taxonomy import MoodTaxonomy


class APIServerHandler(BaseHTTPRequestHandler):
    """Handles REST API requests from the React GUI."""

    taxonomy = MoodTaxonomy()

    def _set_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_json_response(self, data: Any, status: int = HTTPStatus.OK) -> None:
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_error_response(self, message: str, status: int = HTTPStatus.BAD_REQUEST, details: Optional[Any] = None) -> None:
        payload = {"error": message}
        if details:
            payload["details"] = details
        self._send_json_response(payload, status=status)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._set_cors_headers()
        self.end_headers()

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON payload: {e}") from e

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip("/")

        if path in ("", "/api", "/api/health"):
            self._send_json_response({
                "status": "ok",
                "service": "Mood-Based Spotify Playlist Generator API",
                "version": "0.1.0",
            })
            return

        if path == "/api/config":
            try:
                cfg = load_config()
                self._send_json_response({
                    "song_count": cfg.song_count,
                    "output_format": cfg.output_format,
                })
            except Exception as e:
                self._send_error_response(f"Failed to load configuration: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/taxonomy":
            try:
                core_list = []
                for name in self.taxonomy.core_emotions:
                    core = self.taxonomy.get_core_emotion(name)
                    branches_data = []
                    for b_name in self.taxonomy.get_branches(name):
                        branch = self.taxonomy.get_branch(name, b_name)
                        branches_data.append({
                            "name": branch.name,
                            "description": branch.description,
                            "specific_emotions": branch.specific_emotions,
                        })
                    core_list.append({
                        "name": core.name,
                        "code_letter": core.code_letter,
                        "description": core.description,
                        "branches": branches_data,
                    })

                intensity_levels = [
                    {
                        "min": lvl.range[0],
                        "max": lvl.range[1],
                        "label": lvl.label,
                        "description": lvl.description,
                    }
                    for lvl in self.taxonomy.get_intensity_levels()
                ]

                self._send_json_response({
                    "core_emotions": core_list,
                    "intensity_levels": intensity_levels,
                    "intensity_min": self.taxonomy.intensity_min,
                    "intensity_max": self.taxonomy.intensity_max,
                })
            except Exception as e:
                self._send_error_response(f"Failed to load taxonomy: {e}", status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if path == "/api/spotify/status":
            try:
                spotify = SpotifyClient()
                is_auth = spotify.validate_cached_token()
                user_info = None
                display_name = ""
                user_id = ""
                if is_auth:
                    profile = spotify.user_profile or spotify.get_current_user_profile()
                    user_id = profile.get("id", "Unknown")
                    display_name = profile.get("display_name") or user_id
                    user_info = {
                        "id": user_id,
                        "display_name": display_name,
                    }

                self._send_json_response({
                    "authenticated": is_auth,
                    "display_name": display_name if is_auth else None,
                    "user_id": user_id if is_auth else None,
                    "user": user_info,
                })
            except Exception as e:
                self._send_error_response(f"Failed to retrieve Spotify status: {e}")
            return

        if path == "/api/spotify/auth/start":
            try:
                spotify = SpotifyClient()
                auth_url = spotify.get_authorize_url()
                start_oauth_callback_listener(spotify.redirect_uri)
                self._send_json_response({"auth_url": auth_url})
            except Exception as e:
                self._send_error_response(f"Failed to initiate Spotify authentication: {e}")
            return

        self._send_error_response(f"Endpoint not found: {self.path}", status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip("/")

        try:
            body = self._read_json_body()
        except ValueError as e:
            self._send_error_response(str(e), status=HTTPStatus.BAD_REQUEST)
            return

        if path == "/api/profile":
            try:
                if "code" in body and body["code"]:
                    profile = self.taxonomy.parse_code(body["code"])
                else:
                    core_val = body.get("core_emotion") if body.get("core_emotion") is not None else body.get("core_index")
                    branch_val = body.get("branch") if body.get("branch") is not None else body.get("branch_index")
                    specific_val = body.get("specific_emotion") if body.get("specific_emotion") is not None else body.get("specific_index")
                    intensity = int(body.get("intensity", 5))

                    if core_val is None or branch_val is None or specific_val is None:
                        raise ValueError("Missing core, branch, or specific emotion parameters.")

                    # Resolve core index
                    if isinstance(core_val, str):
                        core_names = list(self.taxonomy.core_emotions)
                        if core_val not in core_names:
                            raise ValueError(f"Unknown core emotion '{core_val}'")
                        core_idx = core_names.index(core_val) + 1
                    else:
                        core_idx = int(core_val)

                    core_name = self.taxonomy.get_core_emotion(core_idx).name

                    # Resolve branch index
                    if isinstance(branch_val, str):
                        branches = self.taxonomy.get_branches(core_name)
                        if branch_val not in branches:
                            raise ValueError(f"Unknown branch '{branch_val}'")
                        branch_idx = branches.index(branch_val) + 1
                    else:
                        branch_idx = int(branch_val)

                    branch_name = self.taxonomy.get_branch(core_name, branch_idx).name

                    # Resolve specific emotion index
                    if isinstance(specific_val, str):
                        specifics = self.taxonomy.get_specific_emotions(core_name, branch_name)
                        if specific_val not in specifics:
                            raise ValueError(f"Unknown specific emotion '{specific_val}'")
                        specific_idx = specifics.index(specific_val) + 1
                    else:
                        specific_idx = int(specific_val)

                    profile = self.taxonomy.build_mood_profile(
                        core_index=core_idx,
                        branch_index=branch_idx,
                        specific_index=specific_idx,
                        intensity=intensity,
                    )
                self._send_json_response(profile.to_dict())
            except Exception as e:
                self._send_error_response(f"Failed to generate mood profile: {e}")
            return

        if path == "/api/prompt":
            try:
                profile_data = body.get("profile")
                if not profile_data:
                    self._send_error_response("Missing 'profile' in request body.")
                    return

                code = profile_data.get("code")
                profile = self.taxonomy.parse_code(code) if code else MoodProfile(**profile_data)
                cfg = load_config()
                song_count = body.get("song_count", cfg.song_count)
                output_format = body.get("output_format", cfg.output_format)

                prompt = generate_recommendation_prompt(
                    profile=profile,
                    song_count=song_count,
                    output_format=output_format,
                )
                self._send_json_response({
                    "prompt": prompt,
                    "song_count": song_count,
                    "output_format": output_format,
                    "mood_code": profile.code,
                })
            except Exception as e:
                self._send_error_response(f"Failed to generate prompt: {e}")
            return

        if path == "/api/songs/parse":
            try:
                raw_text = body.get("raw_text", "")
                format_hint = body.get("format_hint")
                songs = parse_song_list(raw_text, format_hint=format_hint)
                self._send_json_response({
                    "valid": True,
                    "count": len(songs),
                    "songs": [{"title": s.title, "artist": s.artist} for s in songs],
                })
            except SongParseError as e:
                self._send_json_response({
                    "valid": False,
                    "error": str(e),
                    "songs": [],
                }, status=HTTPStatus.UNPROCESSABLE_ENTITY)
            except Exception as e:
                self._send_error_response(f"Failed to parse songs: {e}")
            return

        if path == "/api/spotify/resolve":
            try:
                song_items = body.get("songs", [])
                if not song_items:
                    self._send_error_response("No songs provided in request.")
                    return

                recs = [SongRecommendation(title=s["title"], artist=s["artist"]) for s in song_items]
                spotify = SpotifyClient()
                resolved, unresolved = spotify.resolve_songs(recs)

                self._send_json_response({
                    "resolved": [
                        {
                            "title": r.title,
                            "artist": r.artist,
                            "spotify_uri": r.spotify_uri,
                            "spotify_id": r.spotify_id,
                            "spotify_url": r.spotify_url,
                            "album_name": r.album_name,
                        }
                        for r in resolved
                    ],
                    "unresolved": [
                        {"title": u.title, "artist": u.artist, "reason": u.reason}
                        for u in unresolved
                    ],
                    "resolved_count": len(resolved),
                    "total_count": len(recs),
                })
            except Exception as e:
                self._send_error_response(f"Spotify resolution failed: {e}")
            return

        if path == "/api/spotify/playlist":
            try:
                profile_data = body.get("profile")
                track_data = body.get("tracks", [])

                if not profile_data or not track_data:
                    self._send_error_response("Missing 'profile' or 'tracks' in request body.")
                    return

                code = profile_data.get("code")
                profile = self.taxonomy.parse_code(code) if code else MoodProfile(**profile_data)
                tracks = [
                    ResolvedTrack(
                        title=t["title"],
                        artist=t["artist"],
                        spotify_uri=t["spotify_uri"],
                        spotify_id=t.get("spotify_id", ""),
                        spotify_url=t.get("spotify_url", ""),
                        album_name=t.get("album_name", ""),
                    )
                    for t in track_data
                ]

                spotify = SpotifyClient()
                result = spotify.create_playlist(profile=profile, tracks=tracks)

                self._send_json_response({
                    "playlist_id": result.playlist_id,
                    "playlist_name": result.playlist_name,
                    "playlist_url": result.playlist_url,
                    "tracks_added": result.success_count,
                    "total_recommendations": result.total_recommendations,
                })
            except Exception as e:
                self._send_error_response(f"Playlist creation failed: {e}")
            return

        if path == "/api/spotify/auth/disconnect":
            try:
                spotify = SpotifyClient()
                spotify.disconnect()
                self._send_json_response({"success": True})
            except Exception as e:
                self._send_error_response(f"Failed to disconnect Spotify: {e}")
            return

        self._send_error_response(f"Endpoint not found: {self.path}", status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress noisy default logging in standard runs."""
        if os.environ.get("SERVER_DEBUG", "").lower() in ("1", "true"):
            super().log_message(format, *args)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handles Spotify OAuth authorization code callbacks."""

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        if "error" in query:
            error_desc = query.get("error", ["Authorization failed"])[0]
            self._render_page(
                title="Spotify Authentication Failed",
                icon="✕",
                icon_bg="#f43f5e",
                heading="Spotify Authentication Failed",
                message=f"Spotify returned an error: {error_desc}. You can close this window and try again.",
                badge="Authorization Error",
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        code = query.get("code", [""])[0]
        if not code:
            self._render_page(
                title="Missing Authorization Code",
                icon="✕",
                icon_bg="#f43f5e",
                heading="Missing Authorization Code",
                message="No authorization code was found in the Spotify redirect. Please try again.",
                badge="Invalid Callback",
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        try:
            spotify = SpotifyClient()
            profile = spotify.exchange_code_for_token(code)
            display_name = profile.get("display_name") or profile.get("id", "Spotify User")
            self._render_page(
                title="Spotify Connected",
                icon="✓",
                icon_bg="#1db954",
                heading="Spotify Connected!",
                message="Authentication was successful. You can close this window and return to the Mood Playlist Generator.",
                badge=f"Connected as {display_name}",
                status=HTTPStatus.OK,
                auto_close=True,
            )
        except Exception as e:
            self._render_page(
                title="Token Exchange Failed",
                icon="✕",
                icon_bg="#f43f5e",
                heading="Token Exchange Failed",
                message=f"Failed to complete authentication: {e}",
                badge="Exchange Error",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def _render_page(
        self,
        title: str,
        icon: str,
        icon_bg: str,
        heading: str,
        message: str,
        badge: str,
        status: int = HTTPStatus.OK,
        auto_close: bool = False,
    ) -> None:
        auto_close_script = "<script>setTimeout(() => { window.close(); }, 3500);</script>" if auto_close else ""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      background: #0d0e12;
      color: #f3f4f6;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
      padding: 1rem;
      box-sizing: border-box;
    }}
    .card {{
      background: #16181f;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 2.5rem 2rem;
      text-align: center;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
    }}
    .icon {{
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: {icon_bg};
      color: #000000;
      font-size: 2rem;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.25rem;
    }}
    h1 {{
      margin: 0 0 0.5rem;
      font-size: 1.5rem;
      color: #ffffff;
    }}
    p {{
      color: #9ca3af;
      font-size: 0.95rem;
      line-height: 1.5;
      margin: 0 0 1.5rem;
    }}
    .badge {{
      display: inline-block;
      background: rgba(29, 185, 84, 0.12);
      border: 1px solid rgba(29, 185, 84, 0.3);
      color: #4ade80;
      padding: 0.4rem 1rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">{icon}</div>
    <h1>{heading}</h1>
    <p>{message}</p>
    <div class="badge">{badge}</div>
  </div>
  {auto_close_script}
</body>
</html>"""
        response_bytes = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format: str, *args: Any) -> None:
        if os.environ.get("SERVER_DEBUG", "").lower() in ("1", "true"):
            super().log_message(format, *args)


_CALLBACK_SERVER: Optional[ThreadingHTTPServer] = None
_CALLBACK_LOCK = threading.Lock()


def start_oauth_callback_listener(redirect_uri: str) -> None:
    """Start local background callback listener for the registered redirect URI."""
    global _CALLBACK_SERVER
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 8888

    with _CALLBACK_LOCK:
        if _CALLBACK_SERVER is not None:
            return
        try:
            server = ThreadingHTTPServer((host, port), OAuthCallbackHandler)
            _CALLBACK_SERVER = server
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
        except OSError:
            # Port may already be in use or bound
            pass


def create_api_server(host: str = "127.0.0.1", port: int = 5000) -> ThreadingHTTPServer:
    """Create and return the HTTP API server instance."""
    server = ThreadingHTTPServer((host, port), APIServerHandler)
    return server


def run_server(host: str = "127.0.0.1", port: int = 5000) -> None:
    """Start the HTTP API server for local GUI communication."""
    server = create_api_server(host=host, port=port)
    print(f"[✓] Backend API Server listening on http://{host}:{port}")
    print("    Press Ctrl+C to stop the server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping API server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_server(port=port)
