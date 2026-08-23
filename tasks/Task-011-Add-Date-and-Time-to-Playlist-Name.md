# Task 011 — Add Date and Time to Playlist Name

## Objective

Update the Spotify playlist naming convention to preserve the existing mood-based format while appending the current date and time.

The existing format is:

Joy — Excited — Energetic

The new format should be:

Joy — Excited — Energetic — Aug 23, 2026 3:42 PM

## Requirements

- Preserve the existing mood hierarchy in the playlist name.
- Append the current local date and time.
- Use a human-readable date and time format.
- Include enough time precision to distinguish playlists generated within the same day.
- Do not add seconds unless necessary.
- The timestamp should be generated when the playlist is created, not when the mood profile is initially selected.
- Do not modify the mood code or mood profile structure.
- Keep the naming logic centralized rather than duplicating formatting logic.
- Update affected tests and documentation.
- Ensure existing tests continue to pass.

Do not make unrelated architectural changes.