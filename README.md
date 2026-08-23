# Mood Profile & Prompt Generator

A reference implementation demonstrating **Context System Design (v0.1)**.

---

## Overview

The **Mood Profile & Prompt Generator** is a lightweight, deterministic command-line application that:

1. Guides the user through the canonical mood taxonomy to capture their emotional state.
2. Constructs a structured **Mood Profile** and canonical mood code (e.g. `J-3-1:8`).
3. Formats the profile into a **static song-recommendation prompt**.
4. Displays the final prompt for the user to copy into an external chatbot for music recommendations.

> **Note on Implementation Scope:**
> Unlike the earlier exploratory design which outlined end-to-end Spotify playlist creation and in-app LLM interpretation, the current application is intentionally simplified to focus on **Context Generation → Context Modeling → Static Prompt Assembly**. The application contains **no internal LLM runtime and no Spotify API integration**.

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
        ↓
Final Output            Completed prompt is displayed for copying into an external chatbot
```

---

## Key Features

* **Authoritative Human-in-the-Loop Selection:** The user explicitly chooses their core emotion, branch, specific emotion, and intensity.
* **Deterministic & Standalone:** Runs locally with zero external network or API dependencies.
* **Modular Prompt Templates:** Prompt templates are cleanly decoupled from CLI traversal logic.
* **Canonical Taxonomy:** Uses [`context/mood-taxonomy.json`](context/mood-taxonomy.json) as the single source of truth.

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

Example interaction:
```text
What are you feeling?
  1. Joy — Feelings of positive valence, contentment, happiness...
  ...
Select core emotion [1-6]: 1

Joy
  1. Content — Calm, satisfied, or restful positive states.
  2. Happy — General uplifted, cheerful, and pleased positive states.
  3. Excited — High-activation, energetic, and eager positive states.
Select branch [1-3]: 3

Excited
  1. Energetic
  2. Enthusiastic
Select specific emotion [1-2]: 1

Emotional Intensity (1–10):
Enter intensity [1-10]: 8

Mood Profile
-------------
Intensity: 8
Core Emotion: Joy
Branch: Excited
Specific Emotion: Energetic
Mood Code: J-3-1:8

Actions: [C]onfirm & Generate Prompt | [E]dit | [R]estart | [Q]uit: c

============================================================
              GENERATED RECOMMENDATION PROMPT
============================================================
Generate 10 song titles based on the following mood profile.

Intensity: 8
Core Emotion: Joy
Branch: Excited
Specific Emotion: Energetic
Mood Code: J-3-1:8

Return the song title and artist for each recommendation.
============================================================
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

### 3. Display Full Taxonomy
```bash
python3 main.py --dump-taxonomy
```

### 4. Run Automated Tests
```bash
python3 -m unittest discover -s tests
```

---

## Project Structure

```text
.
├── AGENTS.md                  # Operating guidelines for AI coding agents
├── README.md                  # Project overview and usage documentation
├── main.py                    # Root entrypoint
├── src/                       # Application source code
│   ├── __init__.py
│   ├── models.py              # MoodProfile and taxonomy data models
│   ├── taxonomy.py            # Taxonomy traversal, validation, and code parsing
│   ├── prompt.py              # Static prompt template representation and rendering
│   ├── mood_selection.py      # Interactive CLI wizard
│   └── cli.py                 # CLI argument parsing
├── tests/                     # Automated unit test suite
│   ├── __init__.py
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
    └── Task-003—Simplify-Application-to-Mood-Profile-Prompt-Generator.md
```
