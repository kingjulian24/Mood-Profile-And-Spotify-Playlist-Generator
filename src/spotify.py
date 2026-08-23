"""Deterministic Spotify Web API client for track resolution and playlist generation."""

from __future__ import annotations
import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.models import MoodProfile, PlaylistResult, ResolvedTrack, SongRecommendation, UnresolvedTrack


SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"
DEFAULT_SCOPE = "playlist-modify-public playlist-modify-private"
DEFAULT_TOKEN_CACHE = Path(__file__).parent.parent / ".cache-spotify.json"


class SpotifyError(Exception):
    """Base exception for Spotify operations."""
    pass


class SpotifyAuthError(SpotifyError):
    """Raised when authentication with Spotify fails or credentials are missing."""
    pass


class SpotifyClient:
    """Handles Spotify API authentication, track search/resolution, and playlist creation."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        token_cache_path: Optional[Path | str] = None,
        http_requester: Optional[Callable[..., Dict[str, Any]]] = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ):
        self.client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET", "")
        self.redirect_uri = redirect_uri or os.environ.get("SPOTIFY_REDIRECT_URI", DEFAULT_REDIRECT_URI)
        self.access_token = access_token or os.environ.get("SPOTIFY_ACCESS_TOKEN", "")
        self.token_cache_path = Path(token_cache_path) if token_cache_path else DEFAULT_TOKEN_CACHE
        self._http_requester = http_requester
        self._input = input_func
        self._print = output_func
        self.refresh_token: Optional[str] = None

    def _http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any] | str | bytes] = None,
    ) -> Dict[str, Any]:
        """Perform an HTTP request returning JSON data."""
        if self._http_requester:
            return self._http_requester(url=url, method=method, headers=headers, data=data)

        req_headers = headers.copy() if headers else {}
        body_bytes: Optional[bytes] = None

        if data is not None:
            if isinstance(data, (dict, list)):
                req_headers["Content-Type"] = "application/json"
                body_bytes = json.dumps(data).encode("utf-8")
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data

        req = urllib.request.Request(url, data=body_bytes, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_bytes = resp.read()
                if not resp_bytes:
                    return {}
                return json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(error_body)
                msg = err_json.get("error_description") or err_json.get("error", {}).get("message") or error_body
            except Exception:
                msg = error_body
            raise SpotifyError(f"Spotify API error ({e.code}): {msg}") from e
        except Exception as e:
            raise SpotifyError(f"HTTP request failed: {e}") from e

    def _load_cached_token(self) -> bool:
        """Attempt to load token from disk cache."""
        if self.token_cache_path.exists():
            try:
                with open(self.token_cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                self.access_token = cache_data.get("access_token", "")
                self.refresh_token = cache_data.get("refresh_token")
                return bool(self.access_token)
            except Exception:
                return False
        return False

    def _save_cached_token(self, token_data: Dict[str, Any]) -> None:
        """Save tokens to disk cache."""
        try:
            with open(self.token_cache_path, "w", encoding="utf-8") as f:
                json.dump(token_data, f)
        except Exception:
            pass

    def authenticate(self) -> None:
        """
        Authenticate with Spotify using available credentials or cached tokens.
        Raises SpotifyAuthError if authentication cannot be completed.
        """
        if self.access_token:
            return

        if self._load_cached_token():
            return

        if not self.client_id or not self.client_secret:
            raise SpotifyAuthError(
                "Spotify credentials not found.\n"
                "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables, "
                "or provide SPOTIFY_ACCESS_TOKEN.\n"
                "See README.md for Spotify developer setup instructions."
            )

        # Generate authorization URL
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": DEFAULT_SCOPE,
        }
        auth_url = f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

        self._print("\n" + "=" * 60)
        self._print("               SPOTIFY AUTHENTICATION")
        self._print("=" * 60)
        self._print("To authenticate with Spotify, open the following URL in your browser:\n")
        self._print(f"  {auth_url}\n")
        self._print("After authorizing, you will be redirected to your redirect URI.")
        self._print("Copy the full redirect URL (or authorization code) and paste it below.")
        self._print("=" * 60)

        redirect_input = self._input("\nEnter redirect URL or code: ").strip()
        if not redirect_input:
            raise SpotifyAuthError("No authorization code provided.")

        code = redirect_input
        if "code=" in redirect_input:
            parsed = urllib.parse.urlparse(redirect_input)
            query = urllib.parse.parse_qs(parsed.query)
            code = query.get("code", [""])[0]

        if not code:
            raise SpotifyAuthError("Failed to extract authorization code from input.")

        # Exchange code for tokens
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = urllib.parse.urlencode({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        })

        token_resp = self._http_request(SPOTIFY_TOKEN_URL, method="POST", headers=headers, data=data)
        self.access_token = token_resp.get("access_token", "")
        self.refresh_token = token_resp.get("refresh_token")

        if not self.access_token:
            raise SpotifyAuthError("Failed to obtain access token from Spotify.")

        self._save_cached_token(token_resp)
        self._print("[✓] Spotify authentication successful.\n")

    def _get_auth_headers(self) -> Dict[str, str]:
        """Return Authorization headers."""
        if not self.access_token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.access_token}"}

    def search_track(self, title: str, artist: str) -> Optional[ResolvedTrack]:
        """
        Search for a track on Spotify by title and artist.
        Returns ResolvedTrack if found, or None.
        """
        # Primary search: field filters track and artist
        query = f'track:"{title}" artist:"{artist}"'
        encoded_query = urllib.parse.urlencode({"q": query, "type": "track", "limit": 5})
        url = f"{SPOTIFY_API_BASE}/search?{encoded_query}"

        try:
            resp = self._http_request(url, headers=self._get_auth_headers())
        except SpotifyError:
            # Fallback free text search
            fallback_query = f"{title} {artist}"
            encoded_query = urllib.parse.urlencode({"q": fallback_query, "type": "track", "limit": 5})
            url = f"{SPOTIFY_API_BASE}/search?{encoded_query}"
            resp = self._http_request(url, headers=self._get_auth_headers())

        items = resp.get("tracks", {}).get("items", [])
        if not items:
            # Try free text search if structured query returned nothing
            fallback_query = f"{title} {artist}"
            encoded_query = urllib.parse.urlencode({"q": fallback_query, "type": "track", "limit": 5})
            url = f"{SPOTIFY_API_BASE}/search?{encoded_query}"
            resp = self._http_request(url, headers=self._get_auth_headers())
            items = resp.get("tracks", {}).get("items", [])

        if not items:
            return None

        # Pick best match: prefer exact match or top ranked result
        best_item = items[0]
        spotify_uri = best_item.get("uri", "")
        spotify_id = best_item.get("id", "")
        spotify_url = best_item.get("external_urls", {}).get("spotify", "")
        track_name = best_item.get("name", title)
        artist_names = ", ".join(a.get("name", "") for a in best_item.get("artists", [])) or artist
        album_name = best_item.get("album", {}).get("name", "")

        return ResolvedTrack(
            title=track_name,
            artist=artist_names,
            spotify_uri=spotify_uri,
            spotify_id=spotify_id,
            spotify_url=spotify_url,
            album_name=album_name,
        )

    def resolve_songs(
        self,
        recommendations: List[SongRecommendation],
    ) -> Tuple[List[ResolvedTrack], List[UnresolvedTrack]]:
        """
        Resolve a list of SongRecommendation objects against Spotify.
        Returns a tuple of (resolved_tracks, unresolved_tracks).
        """
        resolved: List[ResolvedTrack] = []
        unresolved: List[UnresolvedTrack] = []

        for rec in recommendations:
            try:
                track = self.search_track(rec.title, rec.artist)
                if track:
                    resolved.append(track)
                else:
                    unresolved.append(UnresolvedTrack(title=rec.title, artist=rec.artist, reason="No match found on Spotify"))
            except Exception as e:
                unresolved.append(UnresolvedTrack(title=rec.title, artist=rec.artist, reason=str(e)))

        return resolved, unresolved

    def get_current_user_id(self) -> str:
        """Fetch current authenticated user ID from Spotify."""
        resp = self._http_request(f"{SPOTIFY_API_BASE}/me", headers=self._get_auth_headers())
        user_id = resp.get("id")
        if not user_id:
            raise SpotifyError("Unable to retrieve user ID from Spotify profile.")
        return user_id

    def create_playlist(
        self,
        profile: MoodProfile,
        tracks: List[ResolvedTrack],
        public: bool = False,
    ) -> PlaylistResult:
        """
        Create a Spotify playlist for the given mood profile and populate it with resolved tracks.
        """
        if not tracks:
            raise SpotifyError("Cannot create a playlist with zero resolved tracks.")

        user_id = self.get_current_user_id()
        playlist_name = profile.format_playlist_name()
        description = (
            f"Generated by Mood Profile & Prompt Generator | "
            f"Mood: {profile.specific_emotion} (Intensity: {profile.intensity}/10, Code: {profile.code})"
        )

        payload = {
            "name": playlist_name,
            "description": description,
            "public": public,
        }

        create_resp = self._http_request(
            f"{SPOTIFY_API_BASE}/users/{user_id}/playlists",
            method="POST",
            headers=self._get_auth_headers(),
            data=payload,
        )

        playlist_id = create_resp.get("id")
        playlist_url = create_resp.get("external_urls", {}).get("spotify", "")

        if not playlist_id:
            raise SpotifyError("Failed to create Spotify playlist.")

        # Add tracks in batches of up to 100
        uris = [t.spotify_uri for t in tracks if t.spotify_uri]
        for i in range(0, len(uris), 100):
            batch = uris[i : i + 100]
            self._http_request(
                f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/tracks",
                method="POST",
                headers=self._get_auth_headers(),
                data={"uris": batch},
            )

        return PlaylistResult(
            playlist_id=playlist_id,
            playlist_name=playlist_name,
            playlist_url=playlist_url,
            resolved_tracks=list(tracks),
            unresolved_tracks=[],
        )
