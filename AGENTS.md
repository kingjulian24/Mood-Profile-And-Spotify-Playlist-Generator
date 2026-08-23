# AGENTS.md — Agent Operating Instructions & Context

Welcome to the **Mood Profile & Prompt Generator** project. This document defines the operating context, architectural boundaries, data contracts, and implementation rules for AI agents contributing to this codebase.

---

## 1. Project Purpose & Scope

The application **determines a structured mood profile through an interactive CLI and generates a prompt that can be submitted to an external chatbot for song recommendations.**

The application itself:
* Does **not** execute LLMs or make external AI API calls.
* Does **not** integrate with the Spotify API, authenticate users, or create playlists.
* Is deterministic, lightweight, and focused on **Context Generation → Context Modeling → Static Prompt Assembly**.

Song recommendations are handled externally by the chatbot that the user provides the generated prompt to.

---

## 2. Core Philosophy & Directives

This project serves as an implementation for **Context System Design (v0.1)**:

1. **The User is the Authority on Their Emotions:**
   The user explicitly selects their emotional state through an interactive, deterministic taxonomy traversal (Core Emotion → Branch → Specific Emotion → Intensity 1–10).

2. **Deterministic Context Modeling:**
   The application maps the user's choices into a structured `MoodProfile` and canonical code (e.g. `J-3-1:8`).

3. **Separation of Template from Interaction:**
   The static prompt template (`src/prompt.py`) is decoupled from the CLI interaction logic (`src/mood_selection.py`).

4. **No Premature Infrastructure:**
   No vector databases, external APIs, LLM runtimes, or complex frameworks.

---

## 3. Architecture & Data Flow

```text
User
 ↓
Interactive CLI (src/mood_selection.py)
 ↓
Taxonomy Traversal (src/taxonomy.py & context/mood-taxonomy.json)
 ↓
Structured Mood Profile (src/models.py: MoodProfile)
 ↓
Static Prompt Template (src/prompt.py: PromptTemplate)
 ↓
Final Recommendation Prompt (displayed for user to copy)
```

---

## 4. Domain Context & Schemas

Domain context files are located in `context/`:

* **Mood Taxonomy & Intensity Scale:** [`context/mood-taxonomy.json`](context/mood-taxonomy.json)
  * **Core Emotions (6):** Joy (`J`), Sadness (`S`), Anger (`A`), Fear (`F`), Disgust (`D`), Surprise (`Su`)
  * **Branches & Specific Emotions:** 2 levels deep per core emotion
  * **Intensity Scale (1–10):** Emotional activation/energy (1–2: Crisis/Exhausted, 3–4: Low, 5–6: Neutral, 7–8: Positive/Stable, 9–10: Peak State)
  * **Mood Codes:** Format `CORE_CODE-BRANCH_IDX-SPECIFIC_IDX:INTENSITY` (e.g., `J-3-1:8`)
* **Mood Profile Schema:** [`context/schemas/mood-selection.json`](context/schemas/mood-selection.json)

---

## 5. Development Guidelines

1. **Keep It Deterministic & Modular:**
   All taxonomy queries and prompt formatting must be deterministic and testable without network access.
2. **Single Source of Truth:**
   Always use [`context/mood-taxonomy.json`](context/mood-taxonomy.json) for taxonomy structure.
3. **Unit Testing:**
   Maintain test coverage across taxonomy traversal, invalid input handling, profile formatting, and prompt rendering.
