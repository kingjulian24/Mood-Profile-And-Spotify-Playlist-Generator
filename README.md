# Mood-Based Spotify Playlist Generator

A reference implementation and experimental platform for **Context System Design (v0.1)**.

---

## Overview

The **Mood-Based Spotify Playlist Generator** creates personalized Spotify playlists based on structured emotional context. The user interactively selects their mood through a deterministic traversal of the canonical mood taxonomy (Core Emotion → Branch → Specific Emotion → Intensity 1–10). This explicit human-generated context is structured into a canonical mood representation (e.g., `J-3-1:8`) and used as authoritative context to generate, verify, and assemble a Spotify playlist.

### The Central Hypothesis

> **An AI system that receives explicitly modeled, structured, and validated emotional context will produce more relevant, coherent, and explainable music recommendations than an AI system that receives only an unstructured prompt.**

---

## Context System Design Lifecycle

This project treats context as a primary engineering discipline through the **Context System Design Lifecycle**:

```text
Context Generation      User interacts with the Mood Selection CLI
        ↓
Context Modeling        Application models selection into structured taxonomy path & code (e.g. J-3-1:8)
        ↓
Context Validation      User confirms, edits, or restarts their selection before finalizing
        ↓
Context Assembly        Verified mood context formatted for the recommendation engine
        ↓
AI Reasoning            AI generates candidate songs matching verified emotional state
        ↓
External Validation     Application verifies track existence and metadata via Spotify API
        ↓
Context Delivery        Application creates and populates Spotify playlist
        ↓
Evaluation              System logs end-to-end trace to evaluate recommendation quality
        ↓
Context Evolution       Taxonomy, prompts, and scoring criteria refine over time
```

---

## Key Principles & Authority Model

### 1. Human-in-the-Loop Authority Boundary
* **The User is the sole authority** on their personal emotional state. The user explicitly selects their emotion through guided taxonomy traversal rather than relying on probabilistic LLM interpretation.
* **Spotify is the sole authority** on track availability, metadata, and playlist creation. The AI's song suggestions are *candidates*, not verified tracks, until resolved via the Spotify API.
* **The AI is the reasoning bridge** connecting structured emotional context with music recommendations.

```text
User  ────────►  Verified Mood Context  ────────►  AI Recommendation  ────────►  Spotify Catalog Verification  ────────►  Playlist
(Authoritative               (Authoritative                         (Authoritative
 on Emotion)                  Context)                               on Catalog)
```

### 2. Deterministic Mood Selection
The mood selection workflow is entirely deterministic and dynamic:
* Dynamically loads [`context/mood-taxonomy.json`](context/mood-taxonomy.json) as the single source of truth.
* Progressively guides the user: **Core Emotion (1–6) → Branch → Specific Emotion → Intensity (1–10)**.
* Produces canonical mood codes such as `J-3-1:8` (Joy → Excited → Energetic, Intensity: 8).
* Allows navigating backward, editing specific steps, or restarting.

### 3. Separation of Concerns
* **CLI & Application Code:** Handles deterministic operations (taxonomy traversal, input validation, Spotify API queries, playlist CRUD, token management, schema validation, telemetry).
* **AI Agent:** Receives verified mood context to generate 20–30 candidate tracks with fit reasoning.

### 4. No Premature Infrastructure
Adheres to the principle of **preferring existing solutions**. Keeps components lean, modular, and testable without unnecessary frameworks.

---

## Mood Model & Taxonomy

### Intensity Scale (1–10)
Measures **emotional energy / activation**, independent of valence:
* **1–2:** Crisis / Exhausted
* **3–4:** Low / Uncomfortable
* **5–6:** Neutral / Baseline
* **7–8:** Positive / Stable
* **9–10:** Peak State

### Canonical Taxonomy
* **Joy [J]**
  * *Content* (Peaceful, Satisfied)
  * *Happy* (Blissful, Pleased)
  * *Excited* (Energetic, Enthusiastic)
* **Sadness [S]**
  * *Lonely* (Isolated, Abandoned)
  * *Vulnerable* (Fragile, Insecure)
  * *Sluggish* (Heavy, Tired)
* **Anger [A]**
  * *Irritated* (Annoyed, Frustrated)
  * *Resentful* (Envious, Bitter)
  * *Furious* (Enraged, Hostile)
* **Fear [F]**
  * *Anxious* (Overwhelmed, Worried)
  * *Scared* (Terrified, Helpless)
  * *Insecure* (Inadequate, Inferior)
* **Disgust [D]**
  * *Repelled* (Horrified, Nauseated)
  * *Disapproving* (Judgmental, Disappointed)
* **Surprise [Su]**
  * *Amazed* (Astonished, Awed)
  * *Confused* (Disoriented, Perplexed)

*(Machine-readable taxonomy available at [`context/mood-taxonomy.json`](context/mood-taxonomy.json))*

---

## Usage

### Interactive Mood Selection CLI
Run the interactive CLI to select your emotional state:
```bash
python3 main.py
```

### Direct Code Validation & JSON Output
Parse and validate a mood code directly (useful for scripts and pipelines):
```bash
python3 main.py --code J-3-1:8 --json
```

Output:
```json
{
  "code": "J-3-1:8",
  "intensity": 8,
  "core_emotion": "Joy",
  "branch": "Excited",
  "specific_emotion": "Energetic",
  "intensity_label": "Positive / Stable",
  "intensity_description": "High constructive energy, engagement, optimism, or steady excitement.",
  "taxonomy_path": {
    "core_index": 1,
    "branch_index": 3,
    "specific_index": 1,
    "core_emotion": "Joy",
    "branch": "Excited",
    "specific_emotion": "Energetic"
  }
}
```

### Display Full Taxonomy
```bash
python3 main.py --dump-taxonomy
```

### Running Tests
Execute the unit test suite:
```bash
python3 -m unittest discover -s tests
```

---

## Project Structure

```text
.
├── AGENTS.md                  # Operating context and guidelines for AI coding agents
├── README.md                  # Project overview and architectural reference
├── main.py                    # Application entrypoint
├── src/                       # Application source code
│   ├── __init__.py
│   ├── models.py              # Data models (MoodSelection, CoreEmotion, Branch, etc.)
│   ├── taxonomy.py            # Taxonomy loader, tree navigator, code parser & validator
│   ├── mood_selection.py      # Interactive step-by-step CLI workflow
│   └── cli.py                 # CLI argument parsing and runner
├── tests/                     # Automated unit test suite
│   ├── __init__.py
│   ├── test_taxonomy.py       # Unit tests for taxonomy traversal and validation
│   └── test_mood_selection.py # Unit tests for interactive CLI flows and input handling
├── context/                   # Structured domain context and schemas
│   ├── mood-taxonomy.json     # Canonical mood taxonomy and intensity scales
│   └── schemas/               # JSON schemas for data contracts & traceability
│       ├── mood-selection.json
│       ├── song-candidates.json
│       └── execution-trace.json
├── frameworks/                # Foundational framework specifications
│   └── context-system-design-v0.1.md
├── designs/                   # System design documents and specifications
│   └── Mood-Based Spotify Playlist Generator.md
└── tasks/                     # Task definitions and milestones
    ├── Task-001-Initialize-Project-Documentation.md
    └── Task-002—Implement-Interactive-Mood-Selection-CLI.md
```

---

## Documentation & References

* [Context System Design v0.1](frameworks/context-system-design-v0.1.md)
* [Application Design Document](designs/Mood-Based%20Spotify%20Playlist%20Generator.md)
* [Agent Operating Guidelines](AGENTS.md)
