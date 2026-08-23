# AGENTS.md — Agent Operating Instructions & Context

Welcome to the **Mood-Based Spotify Playlist Generator** project. This document defines the operating context, architectural boundaries, data contracts, and implementation rules for AI agents contributing to this codebase.

---

## 1. Project Philosophy & Core Directives

This project serves as a reference implementation for **Context System Design (v0.1)**. When developing or modifying code, adhere strictly to the following principles:

1. **The Model is Not the System:**
   The language model is a reasoning engine within a structured context pipeline. High output quality comes from carefully engineering what information is discovered, structured, validated, and supplied to the model.

2. **The User is the Authority on Their Emotions:**
   The user explicitly selects their emotional state through an interactive, deterministic taxonomy traversal. The application captures the user's authoritative emotional context (Core Emotion, Branch, Specific Emotion, and Intensity 1–10) rather than relying on probabilistic LLM interpretation.

3. **Spotify is the Authority on Catalog & Tracks:**
   AI-generated songs are **candidates** until validated against the Spotify Web API. Never assume a hallucinated or misremembered track exists. Track validation and playlist creation must be handled deterministically.

4. **Prefer Existing Solutions & Avoid Premature Infrastructure:**
   Do not introduce vector databases, complex microservices, RAG pipelines, or unnecessary frameworks unless a concrete requirement is established. Keep components lean, modular, and testable.

5. **Maintain End-to-End Traceability:**
   Every run must maintain a traceable link from user mood selection to candidate generation, Spotify validation, and final playlist assembly.

---

## 2. System Architecture & Responsibilities

The system is divided into strict agentic (probabilistic/reasoning) and programmatic (deterministic) boundaries:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    Deterministic Application Logic                     │
├───────────────────────────────┬────────────────────────────────────────┤
│ Interactive Mood Selection    │ • Dynamic traversal of taxonomy tree   │
│ CLI Component                 │ • Guides user: Core -> Branch ->       │
│                               │   Specific -> Intensity (1-10)         │
│                               │ • Generates canonical code (e.g.       │
│                               │   J-3-1:8) and structured context      │
│                               │ • User confirmation / edit / restart   │
├───────────────────────────────┼────────────────────────────────────────┤
│ Spotify Integration Service   │ • Searches Spotify API for candidates  │
│                               │ • Resolves and validates track URIs    │
│                               │ • Filters unresolvable tracks          │
│                               │ • Creates & populates playlist         │
├───────────────────────────────┼────────────────────────────────────────┤
│ Traceability & Logging        │ • Records full pipeline telemetry      │
│                               │ • Powers quality & context evaluation  │
└───────────────────────────────┴────────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        AI Reasoning Boundaries                         │
├───────────────────────────────┬────────────────────────────────────────┤
│ Recommendation Agent          │ • Receives verified mood context       │
│                               │ • Generates 20–30 candidate tracks     │
│                               │ • Provides reasoning for song choices  │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Domain Context & Schemas

Domain context files are located in `context/`. Agents must use these files as the authoritative source of truth.

### Mood Taxonomy & Intensity Scale
Refer to [`context/mood-taxonomy.json`](context/mood-taxonomy.json) for the canonical hierarchy:
* **Core Emotions (6):** Joy, Sadness, Anger, Fear, Disgust, Surprise
* **Branches & Specific Emotions:** 2 levels deep per core emotion
* **Intensity Scale (1–10):** Emotional energy/activation (1–2: Crisis/Exhausted, 3–4: Low, 5–6: Neutral, 7–8: Positive/Stable, 9–10: Peak State)
* **Mood Codes:** Canonical format `CORE_CODE-BRANCH_IDX-SPECIFIC_IDX:INTENSITY` (e.g., `J-3-1:8`)

### Data Contracts (Schemas in `context/schemas/`)

#### 1. Mood Selection Output
The interactive CLI produces structured output matching [`context/schemas/mood-selection.json`](context/schemas/mood-selection.json):
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

#### 2. Candidate Track Output
When generating recommendations, produce structured candidates matching [`context/schemas/song-candidates.json`](context/schemas/song-candidates.json):
```json
{
  "verified_mood": {
    "intensity": 8,
    "core_emotion": "Joy",
    "branch": "Excited",
    "specific_emotion": "Energetic"
  },
  "candidates": [
    {
      "title": "September",
      "artist": "Earth, Wind & Fire",
      "genre": "Disco / Funk",
      "fit_reasoning": "High-energy rhythm matching intensity 8, joyful and uplifting themes."
    }
  ]
}
```

#### 3. Execution Trace Record
Every run produces an auditable trace matching [`context/schemas/execution-trace.json`](context/schemas/execution-trace.json) for evaluation.

---

## 4. Failure Mode Protocols

When implementing or debugging, ensure the following failure handlers are active:

| Failure Mode | Scenario | Required Handling Protocol |
| :--- | :--- | :--- |
| **Invalid Selection** | User inputs out-of-range choice in CLI | Re-prompt with valid bounds; preserve current step state. |
| **Taxonomy Gap** | User feels emotion outside current tree | Allow back navigation, restart, or graceful exit. |
| **Spotify Search Miss** | Candidate track not found on Spotify | Drop candidate, log miss, and fall back to next ranked candidate track. |
| **Coherence Failure** | Songs individually fit but clash together | Ensure candidate generation prompt balances diversity and sonic coherence. |

---

## 5. Development Guidelines & Rules for Agents

1. **Read Canonical Documents First:**
   * Framework: [`frameworks/context-system-design-v0.1.md`](frameworks/context-system-design-v0.1.md)
   * System Design: [`designs/Mood-Based Spotify Playlist Generator.md`](designs/Mood-Based%20Spotify%20Playlist%20Generator.md)
   * Domain Context: [`context/mood-taxonomy.json`](context/mood-taxonomy.json)

2. **Incremental Development:**
   * Work strictly within the scope of assigned tasks (in `tasks/`).
   * Keep taxonomy traversal deterministic and dynamic (load from JSON, do not hardcode hierarchy).
   * Write unit tests for all taxonomy queries, code formatting, and user input validation.

3. **Security & Secrets:**
   * Never hardcode Spotify API credentials (`client_id`, `client_secret`) or user tokens.
   * Use environment variables via `.env` (ensure `.env` is ignored by Git).

4. **Documentation Integrity:**
   * Keep `README.md`, `AGENTS.md`, and task files updated when architectural decisions evolve.
