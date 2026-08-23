# Task 013 — Implement Mood Selection UI

## Objective

Implement the mood-selection portion of the React GUI.

Replace the mood-selection portion of the CLI workflow with a graphical
interface while preserving the existing Python taxonomy and mood-profile
logic as the source of truth.

## Instructions

Read the following documents before beginning:

- `frameworks/context-system-design-v0.1.md`
- `designs/Mood-Based Spotify Playlist Generator.md`
- `designs/Mood-Based-Spotify-Playlist-Generator-GUI.md`
- `AGENTS.md`
- `README.md`

Inspect the existing GUI architecture and API implementation before making
changes.

## Workflow

The user should progressively select:

1. Core Emotion
2. Branch
3. Specific Emotion
4. Intensity

The available options for each selection should depend on the previous
selection.

For example:

```text
Core Emotion
    ↓
Joy

Branch
    ↓
Happy

Specific Emotion
    ↓
Blissful

Intensity
    ↓
7
````

After all selections are made, the application should generate and display
the resulting Mood Profile.

## Requirements

### Core Emotion

Display the available core emotions from the canonical taxonomy.

Do not hardcode the taxonomy into React.

The taxonomy must come from:

`context/mood-taxonomy.json`

or the existing backend taxonomy API.

### Branch

Once a core emotion is selected, display only the branches belonging to that
emotion.

### Specific Emotion

Once a branch is selected, display only the specific emotions belonging to
that branch.

### Intensity

Allow the user to select an intensity from 1–10.

Use the existing intensity definitions from the canonical taxonomy.

### Mood Profile

After all selections are complete, display:

```text
Intensity: 7
Core Emotion: Joy
Branch: Happy
Specific Emotion: Blissful
Mood Code: J-2-1:7
```

The profile should be generated using the existing Python application logic.

Do not duplicate mood-code generation or taxonomy logic in JavaScript.

## User Interaction

The interface should make the progression obvious.

The user should be able to change any previous selection without restarting
the application.

Changing an earlier selection should invalidate dependent selections where
necessary.

For example:

```text
Joy
  ↓
Happy
  ↓
Blissful
```

If the user changes `Joy` to `Sadness`, the previously selected `Happy` and
`Blissful` values must no longer remain selected if they are invalid.

## Visual Design

Follow the dark visual design established in Task 012.

Keep the interface:

* Clean
* Modern
* Minimal
* Easy to scan

Do not introduce unnecessary animations or decorative elements.

## Scope

This task is limited to mood selection and mood-profile display.

Do not implement:

* Recommendation prompt UI
* Song recommendation input
* Song parsing UI
* Spotify playlist creation UI
* Spotify authentication UI
* New backend infrastructure
* LLM integration

Those will be handled by later tasks.

## CLI

Do not remove or modify the existing CLI workflow unless required to share
existing domain logic.

The CLI must continue functioning.

## Testing

Add or update tests as appropriate.

Verify:

1. Core emotions are loaded from the backend.
2. Branches update based on the selected core emotion.
3. Specific emotions update based on the selected branch.
4. Intensity can be selected from 1–10.
5. The resulting mood profile is correct.
6. Changing an earlier selection resets invalid dependent selections.
7. Existing Python tests continue to pass.
8. The React application builds successfully.

## Cleanup

Do not duplicate taxonomy or mood-profile logic in the frontend.

Remove any unnecessary frontend implementation introduced during this task.

Keep the implementation limited to the scope described above.

