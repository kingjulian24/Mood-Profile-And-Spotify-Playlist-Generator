# Task 002 — Implement Interactive Mood Selection CLI

Update the application to replace LLM-based mood interpretation with an interactive, deterministic mood-selection workflow.

Before beginning, read and follow:

* `AGENTS.md`
* `frameworks/context-system-design-v0.1.md`
* `designs/Mood-Based Spotify Playlist Generator.md`
* `context/mood-taxonomy.json`
* `context/schemas/mood-interpretation.json`

The existing taxonomy is the source of truth.

## Objective

Create a command-line interface that walks the user through the mood taxonomy and produces a structured mood representation.

The user should not need to memorize the taxonomy or its codes.

The application should guide the user through the hierarchy interactively.

## Interaction

The CLI should progressively present the available choices.

### Step 1 — Core Emotion

Present the six core emotions:

```text
1. Joy
2. Sadness
3. Anger
4. Fear
5. Disgust
6. Surprise
```

The user's selection determines the first part of the mood code.

### Step 2 — Branch

After selecting a core emotion, present only the branches belonging to that emotion.

For example, selecting Joy presents:

```text
1. Content
2. Happy
3. Excited
```

The user's selection determines the second part of the code.

### Step 3 — Specific Emotion

After selecting a branch, present the specific emotions belonging to that branch.

For example:

```text
1. Energetic
2. Enthusiastic
```

The user's selection determines the third part of the code.

### Step 4 — Intensity

Ask the user to provide an intensity from 1–10 using the project's existing intensity scale.

The final representation should combine the taxonomy path and intensity.

For example:

```text
J-3-1:8
```

represents:

```text
Joy
└── Excited
    └── Energetic

Intensity: 8
```

The exact internal representation should follow the existing project schemas and conventions.

## Requirements

The implementation must:

1. Use `context/mood-taxonomy.json` as the source of truth rather than duplicating the taxonomy in application logic.
2. Dynamically determine the available choices at each level of the hierarchy.
3. Prevent invalid selections.
4. Require a valid intensity from 1–10.
5. Produce a structured mood representation that can be passed to later stages of the application.
6. Provide a clear summary of the selected mood before completing the interaction.
7. Allow the user to correct or restart their selection before completion.
8. Keep this workflow deterministic; an LLM should not be used to classify the user's mood.
9. Keep the implementation modular so the resulting mood context can later be consumed by the recommendation system.

## Context System Design

This task implements the **Context Generation** and **Context Modeling** portions of the Context System Design lifecycle.

The user is directly generating the emotional context, while the application models that context using the canonical taxonomy.

The application should not infer emotional state beyond what the user explicitly selects.

The resulting structured mood context will become input to later stages of the system.

## Scope

Implement the interactive mood-selection workflow and the supporting data handling required for it.

Do not implement:

* LLM song recommendation
* Spotify integration
* Playlist creation
* Automatic mood inference

Those will be handled by subsequent tasks.

## Testing

Add appropriate tests for the deterministic behavior of the mood-selection component, including:

* Valid core emotion selection.
* Valid branch selection.
* Valid specific emotion selection.
* Invalid selections.
* Invalid intensity values.
* Correct construction of the final mood representation.
* Correct traversal of the taxonomy.

## Documentation

Update project documentation only where necessary to reflect this change in architecture.

In particular, remove or correct any documentation that states that an LLM is responsible for interpreting the user's mood.

The application should now treat the user's explicit taxonomy selection as the authoritative mood input.
