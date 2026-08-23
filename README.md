# Mood-Based Spotify Playlist Generator

A reference implementation and experimental platform for **Context System Design (v0.1)**.

---

## Overview

The **Mood-Based Spotify Playlist Generator** creates personalized Spotify playlists from natural-language descriptions of emotional states. Rather than forcing users into predefined mood categories or slider bars, users express how they feel naturally. The system then interprets, structures, and validates that emotional state with the user before using it as authoritative context to generate, verify, and assemble a Spotify playlist.

### The Central Hypothesis

> **An AI system that explicitly discovers, models, and validates a user's emotional context will produce more relevant, coherent, and explainable music recommendations than an AI system that receives only an unstructured mood description.**

---

## Why Context System Design?

Modern Large Language Models possess strong reasoning capabilities, but their effectiveness depends heavily on the quality and structure of the context they receive. In typical AI applications, context is often fragmented, ambiguous, or treated as ground truth without validation.

This project treats context as a primary engineering discipline through the **Context System Design Lifecycle**:

```text
Context Generation      User expresses emotional state in natural language
        ↓
Context Discovery       AI extracts emotional signals and latent sentiments
        ↓
Context Modeling        AI maps signals to structured taxonomy & intensity (1–10)
        ↓
Context Validation      User confirms, corrects, or clarifies interpretation (HITL)
        ↓
Context Assembly        Verified mood context formatted for recommendation engine
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
* **The User is the sole authority** on their personal emotional state. The AI's classification is an *inference*, never ground truth, until explicitly validated by the user.
* **Spotify is the sole authority** on track availability, metadata, and playlist creation. The AI's song suggestions are *candidates*, not verified tracks, until resolved via the Spotify API.
* **The AI is the reasoning bridge** connecting subjective human emotion with objective music catalogs.

```text
User  ────────►  Verified Mood Context  ────────►  AI Recommendation  ────────►  Spotify Catalog Verification  ────────►  Playlist
(Authoritative               (Authoritative                         (Authoritative
 on Emotion)                  Context)                               on Catalog)
```

### 2. Ambiguity Handling Over False Precision
When a user's prompt is emotionally ambiguous, the AI should present alternative interpretations and ask for clarification rather than forcing an inaccurate classification.

### 3. Separation of Concerns
* **AI Agent:** Handles semantic interpretation, ambiguity detection, candidate generation, and reasoning explanations.
* **Application Code:** Handles deterministic operations (Spotify API queries, playlist CRUD, token management, schema validation, telemetry).

### 4. No Premature Infrastructure
Adheres to the principle of **preferring existing solutions**. Avoids premature integration of vector databases, complex microservices, or heavyweight frameworks until concrete requirements emerge.

---

## Mood Model & Taxonomy

### Intensity Scale (1–10)
Measures **emotional energy / activation**, independent of valence (e.g., high-intensity anger vs high-intensity joy):
* **1–2:** Crisis / Exhausted
* **3–4:** Low / Uncomfortable
* **5–6:** Neutral / Baseline
* **7–8:** Positive / Stable
* **9–10:** Peak State

### Emotional Taxonomy Tree
* **Joy**
  * *Content* (Peaceful, Satisfied)
  * *Happy* (Blissful, Pleased)
  * *Excited* (Energetic, Enthusiastic)
* **Sadness**
  * *Lonely* (Isolated, Abandoned)
  * *Vulnerable* (Fragile, Insecure)
  * *Sluggish* (Heavy, Tired)
* **Anger**
  * *Irritated* (Annoyed, Frustrated)
  * *Resentful* (Envious, Bitter)
  * *Furious* (Enraged, Hostile)
* **Fear**
  * *Anxious* (Overwhelmed, Worried)
  * *Scared* (Terrified, Helpless)
  * *Insecure* (Inadequate, Inferior)
* **Disgust**
  * *Repelled* (Horrified, Nauseated)
  * *Disapproving* (Judgmental, Disappointed)
* **Surprise**
  * *Amazed* (Astonished, Awed)
  * *Confused* (Disoriented, Perplexed)

*(Machine-readable taxonomy available at `context/mood-taxonomy.json`)*

---

## End-to-End Workflow

1. **User Description:** "I feel like I have a ton of energy today. I want to get out, do something, and I'm unusually optimistic."
2. **AI Inference:** Maps to `{ Intensity: 8, Core: Joy, Branch: Excited, Specific: Energetic }`.
3. **User Verification:** User confirms or adjusts the interpretation.
4. **Candidate Generation:** AI generates 20–30 candidate tracks tailored to the verified mood and intensity.
5. **Spotify Track Validation:** Deterministic resolution against Spotify API to verify track URIs and availability.
6. **Playlist Delivery:** 10 validated tracks are assembled into a structured playlist (e.g., `Joy — Excited — Energetic`).
7. **Trace Logging:** Full execution trace recorded for explainability and evaluation.

---

## Project Structure

```text
.
├── AGENTS.md                  # Operating context and guidelines for AI coding agents
├── README.md                  # Project overview and architectural reference
├── frameworks/                # Foundational framework specifications
│   └── context-system-design-v0.1.md
├── designs/                   # System design documents and specifications
│   └── Mood-Based Spotify Playlist Generator.md
├── context/                   # Structured domain context and schemas
│   ├── mood-taxonomy.json     # Canonical mood taxonomy and intensity scales
│   └── schemas/               # JSON schemas for data contracts & traceability
│       ├── mood-interpretation.json
│       ├── song-candidates.json
│       └── execution-trace.json
└── tasks/                     # Task definitions and milestones
    └── Task-001-Initialize-Project-Documentation.md
```

---

## Documentation & References

* [Context System Design v0.1](frameworks/context-system-design-v0.1.md)
* [Application Design Document](designs/Mood-Based%20Spotify%20Playlist%20Generator.md)
* [Agent Operating Guidelines](AGENTS.md)
