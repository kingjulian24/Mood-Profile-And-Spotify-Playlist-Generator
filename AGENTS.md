# AGENTS.md — Agent Operating Instructions & Context

Welcome to the **Mood Profile & Spotify Playlist Generator** project. This document defines the operating context, architectural boundaries, data contracts, and implementation rules for AI agents contributing to this codebase.

---

## 1. Project Purpose & Scope

The application:
1. **Determines a structured mood profile** through an interactive deterministic CLI.
2. **Generates a machine-readable prompt** (`json`, `csv`, or `yaml`) submitted to an external chatbot for song recommendations.
3. **Ingests and parses the chatbot's song recommendations** (`title` and `artist`).
4. **Resolves songs against the Spotify Web API** and creates a Spotify playlist populated with resolved tracks.

The application itself:
* Does **not** execute LLMs or generate song recommendations directly (the user uses an external chatbot for song reasoning).
* Performs all Spotify operations (authentication, catalog searching, track resolution, playlist CRUD) **deterministically**.
* Handles partial resolution gracefully and logs unresolved songs.

---

## 2. Core Philosophy & Directives

This project serves as an implementation for **Context System Design (v0.1)**:

1. **The User is the Authority on Their Emotions:**
   The user explicitly selects their emotional state through an interactive, deterministic taxonomy traversal (Core Emotion → Branch → Specific Emotion → Intensity 1–10).

2. **Deterministic Context Modeling:**
   The application maps the user's choices into a structured `MoodProfile` and canonical code (e.g. `J-3-1:8`).

3. **Machine-Readable Output Contracts:**
   Prompts instruct the external chatbot to return structured song data (`json`, `csv`, or `yaml`) with required `title` and `artist` fields, without conversational prose.

4. **Spotify is the Authority on Catalog and Tracks:**
   Songs returned by external chatbots are treated as unverified candidates until resolved deterministically against the Spotify Web API.

5. **No Premature Infrastructure:**
   No vector databases, external AI runtimes, or unnecessary heavy frameworks.

---

## 3. Architecture & Data Flow

```text
User & Configuration (config.json)
 ↓
Interactive CLI (src/mood_selection.py)
 ↓
Taxonomy Traversal (src/taxonomy.py & context/mood-taxonomy.json)
 ↓
Structured Mood Profile (src/models.py: MoodProfile)
 ↓
Machine-Readable Prompt Template (src/prompt.py: PromptTemplate & src/config.py)
 ↓
External Chatbot Recommendation (Outside Application)
 ↓
Song Ingestion & Validation (src/song_parser.py)
 ↓
Spotify Track Resolution & Playlist Creation (src/spotify.py)
 ↓
Spotify Playlist Result (src/models.py: PlaylistResult)
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
* **Application Configuration:** [`config.json`](config.json)

---

## 5. Development Guidelines

1. **Keep It Deterministic & Modular:**
   All taxonomy queries, parsing, and prompt formatting must be deterministic and testable without live network access.
2. **Mocking External APIs in Tests:**
   All Spotify operations must be tested using test doubles/mocks. Live Spotify credentials must never be required for automated test suites.
3. **Security & Secrets:**
   Never hardcode client IDs, secrets, or access tokens. Use environment variables (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_ACCESS_TOKEN`).
4. **Single Source of Truth:**
   Always use [`context/mood-taxonomy.json`](context/mood-taxonomy.json) for taxonomy structure and [`config.json`](config.json) for user settings.
