"""Interactive command-line interface for mood selection, prompt generation, and Spotify playlist creation."""

from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from src.config import AppConfig, load_config
from src.models import MoodProfile, PlaylistResult, SongRecommendation
from src.prompt import PromptTemplate, generate_recommendation_prompt
from src.song_parser import SongParseError, parse_song_list
from src.spotify import SpotifyClient, SpotifyError
from src.taxonomy import MoodTaxonomy


class MoodSelectionCLI:
    """Guides the user through mood selection, prompt generation, and Spotify playlist creation."""

    def __init__(
        self,
        taxonomy: Optional[MoodTaxonomy] = None,
        config: Optional[AppConfig] = None,
        prompt_template: Optional[PromptTemplate] = None,
        spotify_client: Optional[SpotifyClient] = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ):
        self.taxonomy = taxonomy or MoodTaxonomy()
        self.config = config or load_config()
        self.prompt_template = prompt_template or PromptTemplate()
        self.spotify_client = spotify_client
        self._input = input_func
        self._print = output_func

    def _prompt_choice(
        self,
        prompt_text: str,
        min_val: int,
        max_val: int,
        allow_back: bool = False,
    ) -> Optional[int]:
        """Prompt user for an integer choice in [min_val, max_val] or 'b'/'back'."""
        while True:
            try:
                raw = self._input(prompt_text).strip()
            except (EOFError, KeyboardInterrupt):
                self._print("\nOperation cancelled by user.")
                return None

            if allow_back and raw.lower() in ("b", "back"):
                return -1  # Signal to go back
            if raw.lower() in ("q", "quit", "exit"):
                return None

            try:
                val = int(raw)
                if min_val <= val <= max_val:
                    return val
                self._print(f"  [!] Invalid choice. Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                back_msg = " or 'b' to go back" if allow_back else ""
                self._print(f"  [!] Invalid input. Please enter a valid number ({min_val}–{max_val}){back_msg}.")

    def _read_multiline_input(self) -> str:
        """Read multiline text from user until an empty line or EOF."""
        self._print("\nPaste the chatbot's response below.")
        self._print("(Enter a blank line or press Ctrl+D when finished):")
        lines: List[str] = []
        while True:
            try:
                line = self._input()
                if not line and lines:
                    break
                lines.append(line)
            except EOFError:
                break
        return "\n".join(lines).strip()

    def process_song_import_and_playlist(
        self,
        profile: MoodProfile,
        raw_song_data: Optional[str] = None,
    ) -> Optional[PlaylistResult]:
        """Parse songs, resolve against Spotify, and create a playlist."""
        if not raw_song_data:
            raw_song_data = self._read_multiline_input()

        if not raw_song_data:
            self._print("[!] No song data provided.")
            return None

        # Check if input is a file path
        potential_path = Path(raw_song_data.strip())
        if potential_path.is_file():
            try:
                with open(potential_path, "r", encoding="utf-8") as f:
                    raw_song_data = f.read()
            except Exception as e:
                self._print(f"[!] Failed to read file '{potential_path}': {e}")
                return None

        try:
            recommendations = parse_song_list(raw_song_data, format_hint=self.config.output_format)
            self._print(f"\n[✓] Successfully parsed {len(recommendations)} song recommendation(s).")
        except SongParseError as e:
            self._print(f"\n[!] Failed to parse song list: {e}")
            return None

        spotify = self.spotify_client or SpotifyClient(input_func=self._input, output_func=self._print)

        try:
            self._print("\nResolving tracks against Spotify catalog...")
            resolved, unresolved = spotify.resolve_songs(recommendations)
        except Exception as e:
            self._print(f"\n[!] Spotify resolution error: {e}")
            return None

        self._print(f"\nResolution Results:")
        self._print(f"  • Resolved:   {len(resolved)} / {len(recommendations)} tracks")
        if unresolved:
            self._print(f"  • Unresolved: {len(unresolved)} / {len(recommendations)} tracks")

        if resolved:
            self._print("\nResolved Tracks:")
            for i, track in enumerate(resolved, 1):
                self._print(f"  {i:2d}. {track.title} — {track.artist} ({track.spotify_uri})")

        if unresolved:
            self._print("\nUnresolved Recommendations:")
            for i, unres in enumerate(unresolved, 1):
                self._print(f"  {i:2d}. {unres.title} — {unres.artist} [Reason: {unres.reason}]")

        if not resolved:
            self._print("\n[!] No tracks could be resolved on Spotify. Playlist creation aborted.")
            return None

        try:
            self._print(f"\nCreating Spotify playlist: '{profile.format_playlist_name()}'...")
            playlist_result = spotify.create_playlist(profile=profile, tracks=resolved)
            playlist_result.unresolved_tracks = unresolved

            self._print("\n" + "=" * 60)
            self._print("               SPOTIFY PLAYLIST CREATED")
            self._print("=" * 60)
            self._print(f"  Playlist Name: {playlist_result.playlist_name}")
            self._print(f"  Playlist URL:  {playlist_result.playlist_url}")
            self._print(f"  Tracks Added:  {playlist_result.success_count} / {playlist_result.total_recommendations}")
            self._print("=" * 60 + "\n")
            return playlist_result
        except SpotifyError as e:
            self._print(f"\n[!] Failed to create playlist on Spotify: {e}")
            return None

    def run(self) -> Optional[Tuple[MoodProfile, str]]:
        """
        Run the interactive workflow.
        Returns a tuple of (MoodProfile, generated_prompt) if completed, or None if cancelled.
        """
        self._print("\n" + "=" * 60)
        self._print("             MOOD PROFILE & PROMPT GENERATOR")
        self._print("=" * 60)
        self._print("Select your current emotional state to generate a recommendation prompt.\n")

        core_idx: Optional[int] = None
        branch_idx: Optional[int] = None
        specific_idx: Optional[int] = None
        intensity: Optional[int] = None

        step = 1
        while True:
            # ----------------------------------------------------
            # STEP 1: Core Emotion
            # ----------------------------------------------------
            if step == 1:
                self._print("\nWhat are you feeling?")
                core_emotions = self.taxonomy.core_emotions
                for i, core_name in enumerate(core_emotions, 1):
                    core_obj = self.taxonomy.get_core_emotion(core_name)
                    self._print(f"  {i}. {core_name} — {core_obj.description}")

                choice = self._prompt_choice(
                    f"\nSelect core emotion [1-{len(core_emotions)}] (or 'q' to quit): ",
                    1,
                    len(core_emotions),
                    allow_back=False,
                )
                if choice is None:
                    return None
                core_idx = choice
                branch_idx = None
                specific_idx = None
                step = 2

            # ----------------------------------------------------
            # STEP 2: Branch
            # ----------------------------------------------------
            elif step == 2:
                core_obj = self.taxonomy.get_core_emotion(core_idx)  # type: ignore
                branches = self.taxonomy.get_branches(core_obj.name)

                self._print(f"\n{core_obj.name}")
                for i, b_name in enumerate(branches, 1):
                    b_obj = self.taxonomy.get_branch(core_obj.name, b_name)
                    self._print(f"  {i}. {b_name} — {b_obj.description}")

                choice = self._prompt_choice(
                    f"\nSelect branch [1-{len(branches)}] (or 'b' for back): ",
                    1,
                    len(branches),
                    allow_back=True,
                )
                if choice is None:
                    return None
                if choice == -1:
                    step = 1
                    continue
                branch_idx = choice
                specific_idx = None
                step = 3

            # ----------------------------------------------------
            # STEP 3: Specific Emotion
            # ----------------------------------------------------
            elif step == 3:
                core_obj = self.taxonomy.get_core_emotion(core_idx)  # type: ignore
                b_obj = self.taxonomy.get_branch(core_obj.name, branch_idx)  # type: ignore
                specifics = self.taxonomy.get_specific_emotions(core_obj.name, b_obj.name)

                self._print(f"\n{b_obj.name}")
                for i, s_name in enumerate(specifics, 1):
                    self._print(f"  {i}. {s_name}")

                choice = self._prompt_choice(
                    f"\nSelect specific emotion [1-{len(specifics)}] (or 'b' for back): ",
                    1,
                    len(specifics),
                    allow_back=True,
                )
                if choice is None:
                    return None
                if choice == -1:
                    step = 2
                    continue
                specific_idx = choice
                step = 4

            # ----------------------------------------------------
            # STEP 4: Intensity
            # ----------------------------------------------------
            elif step == 4:
                self._print("\nEmotional Intensity (1–10):")
                for lvl in self.taxonomy.get_intensity_levels():
                    self._print(f"  {lvl.range[0]:2d}–{lvl.range[1]:2d}: {lvl.label} — {lvl.description}")

                choice = self._prompt_choice(
                    "\nEnter intensity [1-10] (or 'b' for back): ",
                    self.taxonomy.intensity_min,
                    self.taxonomy.intensity_max,
                    allow_back=True,
                )
                if choice is None:
                    return None
                if choice == -1:
                    step = 3
                    continue
                intensity = choice
                step = 5

            # ----------------------------------------------------
            # STEP 5: Mood Profile Summary & Confirmation
            # ----------------------------------------------------
            elif step == 5:
                assert core_idx is not None and branch_idx is not None
                assert specific_idx is not None and intensity is not None

                profile = self.taxonomy.build_mood_profile(
                    core_index=core_idx,
                    branch_index=branch_idx,
                    specific_index=specific_idx,
                    intensity=intensity,
                )

                self._print("\n" + profile.format_profile())

                try:
                    action = self._input(
                        "\nActions: [C]onfirm & Generate Prompt | [E]dit a step | [R]estart | [Q]uit: "
                    ).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    self._print("\nOperation cancelled.")
                    return None

                if action in ("c", "confirm", "yes", "y", ""):
                    prompt = generate_recommendation_prompt(
                        profile,
                        config=self.config,
                        template=self.prompt_template,
                    )
                    self._print("\n" + "=" * 60)
                    self._print("              GENERATED RECOMMENDATION PROMPT")
                    self._print("=" * 60)
                    self._print(prompt)
                    self._print("=" * 60)
                    self._print("\nCopy and paste the prompt above into an external chatbot.\n")

                    # Offer to import chatbot song response
                    try:
                        next_action = self._input(
                            "Next: [I]mport chatbot songs & create Spotify playlist | [Q]uit: "
                        ).strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        return profile, prompt

                    if next_action in ("i", "import", "p", "paste"):
                        self.process_song_import_and_playlist(profile)

                    return profile, prompt
                elif action in ("r", "restart"):
                    self._print("\n[i] Restarting selection from Step 1...")
                    step = 1
                elif action in ("e", "edit"):
                    self._print("\nWhich step would you like to edit?")
                    self._print("  1. Core Emotion")
                    self._print("  2. Branch")
                    self._print("  3. Specific Emotion")
                    self._print("  4. Intensity")
                    edit_choice = self._prompt_choice(
                        "Select step to edit [1-4] (or 'b' to return to summary): ",
                        1,
                        4,
                        allow_back=True,
                    )
                    if edit_choice == -1 or edit_choice is None:
                        continue
                    step = edit_choice
                elif action in ("q", "quit", "exit"):
                    self._print("\nSelection cancelled.")
                    return None
                else:
                    self._print("  [!] Unrecognized option. Please choose C, E, R, or Q.")


def select_mood_interactive(
    taxonomy: Optional[MoodTaxonomy] = None,
    config: Optional[AppConfig] = None,
    spotify_client: Optional[SpotifyClient] = None,
) -> Optional[Tuple[MoodProfile, str]]:
    """Convenience function to run the interactive mood selection CLI."""
    cli = MoodSelectionCLI(taxonomy=taxonomy, config=config, spotify_client=spotify_client)
    return cli.run()
