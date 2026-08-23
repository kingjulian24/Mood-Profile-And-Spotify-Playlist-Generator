"""Interactive command-line interface for deterministic mood selection."""

from __future__ import annotations
import sys
from typing import Callable, Optional

from src.models import MoodSelection
from src.taxonomy import MoodTaxonomy


class MoodSelectionCLI:
    """Guides the user through an interactive, step-by-step mood selection process."""

    def __init__(
        self,
        taxonomy: Optional[MoodTaxonomy] = None,
        input_func: Callable[[str], str] = input,
        output_func: Callable[[str], None] = print,
    ):
        self.taxonomy = taxonomy or MoodTaxonomy()
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

    def run(self) -> Optional[MoodSelection]:
        """Run the interactive mood selection workflow."""
        self._print("\n" + "=" * 60)
        self._print("       MOOD-BASED SPOTIFY PLAYLIST GENERATOR")
        self._print("             Interactive Mood Selection")
        self._print("=" * 60)
        self._print("Select your current emotional state using the canonical taxonomy.\n")

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
                self._print("\n--- Step 1: Core Emotion ---")
                self._print("Select the core emotion that best describes how you are feeling:")
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
                # Reset downstream selections if core changed
                branch_idx = None
                specific_idx = None
                step = 2

            # ----------------------------------------------------
            # STEP 2: Branch
            # ----------------------------------------------------
            elif step == 2:
                core_obj = self.taxonomy.get_core_emotion(core_idx)  # type: ignore
                branches = self.taxonomy.get_branches(core_obj.name)

                self._print(f"\n--- Step 2: Emotional Branch for '{core_obj.name}' ---")
                self._print("Select the branch that reflects your state:")
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
                # Reset downstream selection
                specific_idx = None
                step = 3

            # ----------------------------------------------------
            # STEP 3: Specific Emotion
            # ----------------------------------------------------
            elif step == 3:
                core_obj = self.taxonomy.get_core_emotion(core_idx)  # type: ignore
                b_obj = self.taxonomy.get_branch(core_obj.name, branch_idx)  # type: ignore
                specifics = self.taxonomy.get_specific_emotions(core_obj.name, b_obj.name)

                self._print(f"\n--- Step 3: Specific Emotion under '{b_obj.name}' ---")
                self._print("Select the precise emotion:")
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
                self._print("\n--- Step 4: Emotional Intensity (Energy / Activation) ---")
                self._print("Scale of 1–10:")
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
            # STEP 5: Summary & Confirmation
            # ----------------------------------------------------
            elif step == 5:
                assert core_idx is not None and branch_idx is not None
                assert specific_idx is not None and intensity is not None

                selection = self.taxonomy.build_mood_selection(
                    core_index=core_idx,
                    branch_index=branch_idx,
                    specific_index=specific_idx,
                    intensity=intensity,
                )

                self._print("\n" + "=" * 60)
                self._print("                 SELECTED MOOD SUMMARY")
                self._print("=" * 60)
                self._print(f"  Core Emotion:     {selection.core_emotion}")
                self._print(f"  Branch:           {selection.branch}")
                self._print(f"  Specific Emotion: {selection.specific_emotion}")
                self._print(f"  Intensity:        {selection.intensity}/10 ({selection.intensity_label})")
                self._print(f"  Mood Code:        {selection.code}")
                self._print("-" * 60)
                self._print("  Taxonomy Tree:")
                for line in selection.format_tree().split("\n"):
                    self._print(f"    {line}")
                self._print("=" * 60)

                try:
                    action = self._input(
                        "\nActions: [C]onfirm | [E]dit a step | [R]estart | [Q]uit: "
                    ).strip().lower()
                except (EOFError, KeyboardInterrupt):
                    self._print("\nOperation cancelled.")
                    return None

                if action in ("c", "confirm", "yes", "y", ""):
                    self._print(f"\n[✓] Mood confirmed: {selection.code} ({selection.specific_emotion} at intensity {selection.intensity})")
                    return selection
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
) -> Optional[MoodSelection]:
    """Convenience function to run the interactive mood selection CLI."""
    cli = MoodSelectionCLI(taxonomy=taxonomy)
    return cli.run()
