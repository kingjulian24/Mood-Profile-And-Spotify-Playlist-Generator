"""Main CLI entrypoint for Mood-Based Spotify Playlist Generator."""

from __future__ import annotations
import argparse
import sys
from typing import Optional

from src.models import MoodSelection
from src.mood_selection import MoodSelectionCLI
from src.taxonomy import MoodTaxonomy


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Mood-Based Spotify Playlist Generator — Mood Selection CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--code",
        type=str,
        help="Directly parse and validate a mood code (e.g., 'J-3-1:8') without interactive prompts.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the resulting mood selection as structured JSON.",
    )
    parser.add_argument(
        "--dump-taxonomy",
        action="store_true",
        help="Print the full mood taxonomy and intensity scales.",
    )
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """Execute the CLI application."""
    parser = build_parser()
    parsed_args = parser.parse_args(args)

    taxonomy = MoodTaxonomy()

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
        return 0

    selection: Optional[MoodSelection] = None

    if parsed_args.code:
        try:
            selection = taxonomy.parse_code(parsed_args.code)
            if not parsed_args.json:
                print(f"\n[✓] Validated mood code: {parsed_args.code}")
                print(selection.format_tree())
        except Exception as e:
            print(f"Error parsing mood code '{parsed_args.code}': {e}", file=sys.stderr)
            return 1
    else:
        cli = MoodSelectionCLI(taxonomy=taxonomy)
        selection = cli.run()

    if selection is None:
        return 1

    if parsed_args.json:
        print(selection.to_json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
