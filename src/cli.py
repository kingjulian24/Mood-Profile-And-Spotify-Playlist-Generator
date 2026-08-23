"""Main CLI entrypoint for Mood Profile, Prompt Generator, and Spotify Playlist Creator."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Optional

from src.config import ConfigError, load_config
from src.models import MoodProfile
from src.mood_selection import MoodSelectionCLI
from src.prompt import generate_recommendation_prompt
from src.spotify import SpotifyClient
from src.taxonomy import MoodTaxonomy


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Mood Profile & Prompt Generator — Deterministic Music Recommendation & Spotify Playlist Creator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--code",
        type=str,
        help="Directly generate a prompt or playlist from a mood code (e.g., 'J-3-1:8') without interactive prompts.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom configuration file (defaults to config.json).",
    )
    parser.add_argument(
        "--import-songs",
        type=str,
        default=None,
        help="Path to a file containing chatbot-generated song recommendations to import and create a Spotify playlist.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the structured mood profile as JSON.",
    )
    parser.add_argument(
        "--dump-taxonomy",
        action="store_true",
        help="Print the full mood taxonomy and intensity scales.",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start the HTTP API backend server for the React GUI.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port number for the HTTP API backend server.",
    )
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Execute the CLI application."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    try:
        config = load_config(parsed_args.config)
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    try:
        taxonomy = MoodTaxonomy()
    except Exception as e:
        print(f"Taxonomy error: {e}", file=sys.stderr)
        return 1

    if parsed_args.dump_taxonomy:
        print("\n--- Canonical Mood Taxonomy & Intensity Scales ---")
        for core_name in taxonomy.core_emotions:
            core = taxonomy.get_core_emotion(core_name)
            print(f"\n[{core.code_letter}] {core.name}: {core.description}")
            for b_idx, b_name in enumerate(taxonomy.get_branches(core.name), 1):
                branch = taxonomy.get_branch(core.name, b_name)
                print(f"  ├── {b_idx}. {branch.name}: {branch.description}")
                for s_idx, s_name in enumerate(branch.specific_emotions, 1):
                    prefix = "└──" if s_idx == len(branch.specific_emotions) else "├──"
                    print(f"      {prefix} {s_idx}. {s_name}")
    if parsed_args.serve:
        from src.server import run_server
        run_server(port=parsed_args.port)
        return 0

    profile: Optional[MoodProfile] = None
    cli = MoodSelectionCLI(taxonomy=taxonomy, config=config)

    if parsed_args.code:
        try:
            profile = taxonomy.parse_code(parsed_args.code)
            prompt = generate_recommendation_prompt(profile, config=config)
            if not parsed_args.json:
                print("\n" + profile.format_profile())
                print("\n" + "=" * 60)
                print("              GENERATED RECOMMENDATION PROMPT")
                print("=" * 60)
                print(prompt)
                print("=" * 60)
                print("\nCopy and paste the prompt above into an external chatbot.\n")
        except Exception as e:
            print(f"Error parsing mood code '{parsed_args.code}': {e}", file=sys.stderr)
            return 1

        if parsed_args.import_songs:
            cli.process_song_import_and_playlist(profile, raw_song_data=parsed_args.import_songs)
    else:
        result = cli.run()
        if result is None:
            return 1
        profile, _ = result

    if profile is None:
        return 1

    if parsed_args.json:
        print(profile.to_json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
