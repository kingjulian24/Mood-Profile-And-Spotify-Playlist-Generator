# Mood Profile & Prompt Generator

A reference implementation demonstrating **Context System Design (v0.1)**.

---

## Overview

The **Mood Profile & Prompt Generator** is a lightweight, deterministic command-line application that:

1. Guides the user through the canonical mood taxonomy to capture their emotional state.
2. Constructs a structured **Mood Profile** and canonical mood code (e.g. `J-3-1:8`).
3. Formats the profile into a **static song-recommendation prompt** using user-configurable application settings.
4. Displays the final prompt for the user to copy into an external chatbot for music recommendations.

> **Note on Implementation Scope:**
> The application is focused on **Context Generation → Context Modeling → Static Prompt Assembly**. The application contains **no internal LLM runtime and no Spotify API integration**.

---

## Context System Design Lifecycle

```text
Context Generation      User selects mood via the interactive CLI
        ↓
Context Modeling        Application structures choices into a Mood Profile and code (e.g. J-3-1:8)
        ↓
Context Validation      User reviews and confirms the mood profile
        ↓
Prompt Assembly         Static prompt template is populated with the structured mood profile
                        and configured song count (from config.json)
        ↓
Final Output            Completed prompt is displayed for copying into an external chatbot
```

---

## Key Features

* **Authoritative Human-in-the-Loop Selection:** The user explicitly chooses their core emotion, branch, specific emotion, and intensity.
* **Deterministic & Standalone:** Runs locally with zero external network or API dependencies.
* **Dedicated Configuration:** User settings like `song_count` are stored in [`config.json`](config.json).
* **Modular Prompt Templates:** Prompt templates are cleanly decoupled from CLI traversal logic.
* **Canonical Taxonomy:** Uses [`context/mood-taxonomy.json`](context/mood-taxonomy.json) as the single source of truth.

---

## Configuration

Application settings are managed in [`config.json`](config.json) at the root of the project:

```json
{
  "song_count": 10
}
```

### Changing the Number of Songs
To change the number of songs requested in the generated prompt (e.g. to 20), update the `song_count` value in [`config.json`](config.json):

```json
{
  "song_count": 20
}
```

The generated prompt will immediately reflect the new setting (e.g., `"Generate 20 songs based on the following mood profile."`) without requiring any code modifications.

---

## Mood Model & Taxonomy

### Intensity Scale (1–10)
Measures **emotional energy / activation**:
* **1–2:** Crisis / Exhausted
* **3–4:** Low / Uncomfortable
* **5–6:** Neutral / Baseline
* **7–8:** Positive / Stable
* **9–10:** Peak State

### Taxonomy Overview
* **Joy [J]:** Content, Happy, Excited
* **Sadness [S]:** Lonely, Vulnerable, Sluggish
* **Anger [A]:** Irritated, Resentful, Furious
* **Fear [F]:** Anxious, Scared, Insecure
* **Disgust [D]:** Repelled, Disapproving
* **Surprise [Su]:** Amazed, Confused

---

## Usage

### 1. Interactive CLI Mode
Run the interactive wizard:
```bash
python3 main.py
```

### 2. Direct Code Validation & Prompt Generation
Generate a prompt directly from a mood code without interactive prompts:
```bash
python3 main.py --code J-3-1:8
```

Output as structured JSON:
```bash
python3 main.py --code J-3-1:8 --json
```

### 3. Using a Custom Configuration File
```bash
python3 main.py --config path/to/custom_config.json
```

### 4. Display Full Taxonomy
```bash
python3 main.py --dump-taxonomy
```

### 5. Run Automated Tests
```bash
python3 -m unittest discover -s tests
```

---

## Project Structure

```text
.
├── AGENTS.md                  # Operating guidelines for AI coding agents
├── README.md                  # Project overview and usage documentation
├── config.json                # User application configuration (e.g. song_count)
├── main.py                    # Root entrypoint
├── src/                       # Application source code
│   ├── __init__.py
│   ├── config.py              # Configuration loader and validator
│   ├── models.py              # MoodProfile and taxonomy data models
│   ├── taxonomy.py            # Taxonomy traversal, validation, and code parsing
│   ├── prompt.py              # Static prompt template representation and rendering
│   ├── mood_selection.py      # Interactive CLI wizard
│   └── cli.py                 # CLI argument parsing
├── tests/                     # Automated unit test suite
│   ├── __init__.py
│   ├── test_config.py         # Configuration loading and validation tests
│   ├── test_taxonomy.py       # Taxonomy and code parsing tests
│   ├── test_prompt.py         # Prompt template rendering tests
│   └── test_mood_selection.py # Interactive CLI flow tests
├── context/                   # Canonical domain context and schemas
│   ├── mood-taxonomy.json     # Canonical mood taxonomy and intensity scales
│   └── schemas/
│       └── mood-selection.json# JSON schema for MoodProfile
├── frameworks/                # Context System Design framework
│   └── context-system-design-v0.1.md
├── designs/                   # Original reference design document
│   └── Mood-Based Spotify Playlist Generator.md
└── tasks/                     # Task specifications
    ├── Task-001-Initialize-Project-Documentation.md
    ├── Task-002—Implement-Interactive-Mood-Selection-CLI.md
    ├── Task-003—Simplify-Application-to-Mood-Profile-Prompt-Generator.md
    └── Task-004-Add-Application-Configuration.md
```
