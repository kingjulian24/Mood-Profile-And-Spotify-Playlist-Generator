"""Deterministic Spotify Web API client for track resolution and playlist generation."""

from __future__ import annotations
import base64
import json
import os
import time
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
DEFAULT_SCOPE = "playlist-modify-public playlist-modify-private user-read-private"
DEFAULT_TOKEN_CACHE = Path(__file__).parent.parent / ".cache-spotify.json"


class SpotifyError(Exception):
    """Base exception for Spotify operations."""
    pass


class SpotifyAuthError(SpotifyError):
    """Raised when authentication with Spotify fails or credentials are missing."""
    pass


def extract_code_from_input(redirect_input: str) -> str:
    """Extract clean authorization code from raw string or redirect URL."""
    cleaned = redirect_input.strip().strip("'\"")
    if "code=" in cleaned:
        parsed = urllib.parse.urlparse(cleaned)
        query = urllib.parse.parse_qs(parsed.query)
        code = query.get("code", [""])[0]
        if "#" in code:
            code = code.split("#")[0]
        return code.strip()
    if "#" in cleaned:
        cleaned = cleaned.split("#")[0]
    return cleaned.strip()


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
        self.user_profile: Optional[Dict[str, Any]] = None

    def _http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any] | str | bytes] = None,
        retry_on_401: bool = True,
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
                err_obj = err_json.get("error")
                if isinstance(err_obj, dict):
                    msg = err_obj.get("message") or error_body
                elif isinstance(err_obj, str):
                    msg = err_obj
                else:
                    msg = err_json.get("error_description") or error_body
            except Exception:
                msg = error_body

            # Attempt automatic token refresh on 401 Unauthorized
            if e.code == 401 and retry_on_401 and self.refresh_token:
                if self.refresh_access_token():
                    # Retry with new token
                    new_headers = (headers or {}).copy()
                    new_headers["Authorization"] = f"Bearer {self.access_token}"
                    return self._http_request(
                        url=url,
                        method=method,
                        headers=new_headers,
                        data=data,
                        retry_on_401=False,
                    )

            if e.code == 400 and "token" in url:
                msg = f"{msg}. Note: Spotify authorization codes can only be used once and expire quickly. Please generate a new authorization URL if this code was already used."
            elif e.code == 403:
                msg = (
                    f"{msg}. (If your Spotify App is in Development Mode, verify that your account email "
                    f"is registered under 'User Management' in the Spotify Developer Dashboard)."
                )

            raise SpotifyError(f"Spotify API error ({e.code}): {msg}") from e
        except Exception as e:
            if isinstance(e, SpotifyError):
                raise
            raise SpotifyError(f"HTTP request failed: {e}") from e

    def _load_cached_token(self) -> bool:
        """Attempt to load and validate tokens from disk cache."""
        if not self.token_cache_path.exists():
            return False
        try:
            with open(self.token_cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Invalidate cache if client_id does not match
            cached_client_id = cache_data.get("client_id")
            if cached_client_id and self.client_id and cached_client_id != self.client_id:
                return False

            self.access_token = cache_data.get("access_token", "")
            self.refresh_token = cache_data.get("refresh_token")
            return bool(self.access_token)
        except Exception:
            return False

    def _save_cached_token(self, token_data: Dict[str, Any]) -> None:
        """Save tokens to disk cache."""
        try:
            to_save = dict(token_data)
            if self.client_id:
                to_save["client_id"] = self.client_id
            to_save["cached_at"] = time.time()
            with open(self.token_cache_path, "w", encoding="utf-8") as f:
                json.dump(to_save, f)
        except Exception:
            pass

    def _clear_cached_token(self) -> None:
        """Remove invalid token cache file."""
        try:
            if self.token_cache_path.exists():
                self.token_cache_path.unlink()
        except Exception:
            pass

    def refresh_access_token(self) -> bool:
        """Refresh the access token using the stored refresh_token."""
        if not self.refresh_token or not self.client_id or not self.client_secret:
            return False

        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        })

        try:
            token_resp = self._http_request(
                SPOTIFY_TOKEN_URL,
                method="POST",
                headers=headers,
                data=data,
                retry_on_401=False,
            )
            new_access_token = token_resp.get("access_token")
            if new_access_token:
                self.access_token = new_access_token
                if token_resp.get("refresh_token"):
                    self.refresh_token = token_resp["refresh_token"]
                self._save_cached_token({
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires_in": token_resp.get("expires_in", 3600),
                    "scope": token_resp.get("scope", DEFAULT_SCOPE),
                })
                return True
        except Exception:
            pass
        return False

    def get_current_user_profile(self) -> Dict[str, Any]:
        """Fetch current authenticated user profile from Spotify."""
        resp = self._http_request(f"{SPOTIFY_API_BASE}/me", headers=self._get_auth_headers())
        self.user_profile = resp
        return resp

    def authenticate(self) -> None:
        """
        Authenticate with Spotify using available credentials or cached tokens.
        Validates access and displays active user profile diagnostics.
        """
        # Step 1: Check existing access token or load cache
        if not self.access_token:
            self._load_cached_token()

        # Step 2: Validate token if present
        if self.access_token:
            try:
                profile = self.get_current_user_profile()
                user_id = profile.get("id", "Unknown")
                display_name = profile.get("display_name") or user_id
                self._print(f"[✓] Authenticated with Spotify as: {display_name} (User ID: {user_id})")
                return
            except SpotifyError as e:
                # Attempt refresh
                if self.refresh_access_token():
                    try:
                        profile = self.get_current_user_profile()
                        user_id = profile.get("id", "Unknown")
                        display_name = profile.get("display_name") or user_id
                        self._print(f"[✓] Authenticated with Spotify as: {display_name} (User ID: {user_id})")
                        return
                    except Exception:
                        pass
                self._clear_cached_token()
                self.access_token = ""

        # Step 3: Run OAuth Authorization Code Flow
        if not self.client_id or not self.client_secret:
            raise SpotifyAuthError(
                "Spotify credentials not found.\n"
                "Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables, "
                "or provide SPOTIFY_ACCESS_TOKEN.\n"
                "See README.md for Spotify developer setup instructions."
            )

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": DEFAULT_SCOPE,
            "show_dialog": "true",
        }
        auth_url = f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

        self._print("\n" + "=" * 60)
        self._print("               SPOTIFY AUTHENTICATION")
        self._print("=" * 60)
        self._print("To authenticate with Spotify, open the following URL in your browser:\n")
        self._print(f"  {auth_url}\n")
        self._print("After authorizing, you will be redirected to your redirect URI.")
        self._print("Copy the full redirect URL (or authorization code) from your browser and paste it below.")
        self._print("=" * 60)

        redirect_input = self._input("\nEnter redirect URL or code: ").strip()
        if not redirect_input:
            raise SpotifyAuthError("No authorization code provided.")

        code = extract_code_from_input(redirect_input)
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

        token_resp = self._http_request(
            SPOTIFY_TOKEN_URL,
            method="POST",
            headers=headers,
            data=data,
            retry_on_401=False,
        )
        self.access_token = token_resp.get("access_token", "")
        self.refresh_token = token_resp.get("refresh_token")

        if not self.access_token:
            raise SpotifyAuthError("Failed to obtain access token from Spotify.")

        self._save_cached_token(token_resp)

        # Retrieve and log active user diagnostics
        try:
            profile = self.get_current_user_profile()
            user_id = profile.get("id", "Unknown")
            display_name = profile.get("display_name") or user_id
            self._print(f"[✓] Spotify authentication successful: {display_name} (User ID: {user_id})\n")
        except Exception:
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
        if self.user_profile and "id" in self.user_profile:
            return self.user_profile["id"]
        profile = self.get_current_user_profile()
        user_id = profile.get("id")
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

        # POST /v1/me/playlists
        create_resp = self._http_request(
            f"{SPOTIFY_API_BASE}/me/playlists",
            method="POST",
            headers=self._get_auth_headers(),
            data=payload,
        )

        playlist_id = create_resp.get("id")
        playlist_url = create_resp.get("external_urls", {}).get("spotify", "")

        if not playlist_id:
            raise SpotifyError("Failed to create Spotify playlist: response did not include playlist ID.")

        # Add tracks in batches of up to 100
        uris = [t.spotify_uri for t in tracks if t.spotify_uri]
        for i in range(0, len(uris), 100):
            batch = uris[i : i + 100]
            self._http_request(
                f"{SPOTIFY_API_BASE}/playlists/{playlist_id}/items",
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
