# Task 003 — Simplify Application to Mood Profile & Prompt Generator

Read and follow:

* `AGENTS.md`
* `frameworks/context-system-design-v0.1.md`
* `designs/Mood-Based Spotify Playlist Generator.md`
* `context/mood-taxonomy.json`
* `context/schemas/mood-selection.json`

## Objective

Simplify the application so its sole purpose is to:

1. Walk the user through the mood taxonomy using the CLI.
2. Determine the user's mood profile from their selections.
3. Generate a static song-recommendation prompt using that mood profile.
4. Output the completed prompt for the user to copy into an external chatbot.

The application itself must **not use an LLM or any external service**.

The external chatbot will handle song recommendations.

---

## User Workflow

The CLI should guide the user through the mood hierarchy:

```text
Core Emotion
    ↓
Branch
    ↓
Specific Emotion
    ↓
Intensity
    ↓
Mood Profile
    ↓
Generated Prompt
```

For example:

```text
What are you feeling?

1. Joy
2. Sadness
3. Anger
4. Fear
5. Disgust
6. Surprise
```

After selecting **Joy**:

```text
Joy

1. Content
2. Happy
3. Excited
```

After selecting **Excited**:

```text
Excited

1. Energetic
2. Enthusiastic
```

The user then selects an intensity from 1–10.

---

## Mood Profile

The application must produce a structured mood profile containing:

* Intensity
* Core Emotion
* Branch
* Specific Emotion
* Mood Code

For example:

```text
Mood Profile
-------------

Intensity: 8
Core Emotion: Joy
Branch: Excited
Specific Emotion: Energetic
Mood Code: J-3-1:8
```

The mood code must continue to use the existing canonical format.

---

## Prompt Generation

After generating the mood profile, use its values to populate a **static prompt template**.

The prompt should instruct an external chatbot to generate ten song recommendations based on the mood profile.

For example:

```text
Generate 10 song titles based on the following mood profile.

Intensity: 8
Core Emotion: Joy
Branch: Excited
Specific Emotion: Energetic
Mood Code: J-3-1:8

Return the song title and artist for each recommendation.
```

The exact wording of the static template may be improved if necessary, but the application must generate the prompt deterministically.

The LLM is **not** called by the application.

The user will copy the resulting prompt into an external chatbot.

---

## Architecture

The resulting application should be intentionally simple:

```text
User
 ↓
Interactive CLI
 ↓
Mood Selection
 ↓
Structured Mood Profile
 ↓
Static Prompt Template
 ↓
Final Prompt
```

The application ends at the final prompt.

There is no application-side:

* LLM processing
* AI agent
* Song recommendation
* Song candidate generation
* Spotify integration
* Spotify authentication
* Spotify track validation
* Playlist creation
* External API calls

---

## Cleanup Requirement

This task is explicitly a **simplification and cleanup task**, not merely an additive implementation task.

Review the entire existing codebase and remove, consolidate, or simplify any code that does not directly support the new goal.

Do not preserve architecture solely because it was created in previous tasks.

In particular, identify and remove unnecessary abstractions, modules, schemas, dependencies, configuration, tests, and documentation that exist only to support functionality that is no longer part of the application.

The final codebase should reflect the simplified purpose rather than the original Spotify application design.

Do not remove canonical domain context merely because it is not executable code. Retain the mood taxonomy and any schema that remains useful to the current application.

---

## Prompt Template

The prompt template should be represented separately from the CLI interaction logic.

The mood profile should be passed into the template rather than constructed through string manipulation throughout the CLI.

This should make it possible to modify the recommendation prompt later without rewriting the mood-selection workflow.

---

## Testing

Update the test suite to reflect the new application scope.

Tests should cover at minimum:

* Taxonomy traversal.
* Valid mood selection.
* Invalid selections.
* Intensity validation.
* Mood-code generation.
* Mood-profile generation.
* Prompt generation.
* Correct insertion of mood-profile values into the prompt.

Remove tests for functionality that no longer exists.

All tests should pass when the task is complete.

---

## Documentation

Update the current project documentation to accurately describe the simplified application.

`README.md` and `AGENTS.md` should no longer describe the application as a Spotify playlist generator in its current implementation.

They should explain that the application:

> **Determines a structured mood profile through an interactive CLI and generates a prompt that can be submitted to an external chatbot for song recommendations.**

The original design document may remain as the historical/reference design, but the current implementation documentation must clearly distinguish the original goal from the current scope.

---

## Completion Criteria

The task is complete when:

1. Running the application launches the interactive mood-selection workflow.
2. The user selects core emotion, branch, specific emotion, and intensity.
3. The application produces the structured mood profile.
4. The application generates a recommendation prompt from that profile.
5. The final prompt is displayed for the user to copy.
6. No LLM or external API is used.
7. No Spotify functionality remains unless it directly supports the current goal.
8. Unnecessary code from the previous implementation has been removed or simplified.
9. Documentation reflects the new scope.
10. Tests pass.

The final application should be small, deterministic, understandable, and focused exclusively on **mood selection → mood profile → recommendation prompt**.
