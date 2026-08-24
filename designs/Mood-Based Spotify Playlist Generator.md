# Design Document: Mood-Based Spotify Playlist Generator

**Version:** 0.2
**Status:** Draft
**Purpose:** Reference implementation for Context System Design v0.1

---

## 1. Goal

Create an application that generates a Spotify playlist based on the user's current mood.

The user does **not** select a predefined mood or manually assign an intensity.

Instead, the user describes how they currently feel in natural language.

The AI agent then:

1. Interprets the user's description.
2. Maps the description to the application's mood taxonomy.
3. Determines an estimated intensity from 1–10.
4. Presents its interpretation to the user.
5. Allows the user to confirm or correct the interpretation.
6. Uses the verified mood as context for song selection.
7. Generates candidate songs.
8. Verifies the songs against Spotify.
9. Creates the resulting Spotify playlist.

The fundamental interaction is:

```text
User describes mood
        ↓
AI interprets mood
        ↓
Structured mood representation
        ↓
User verifies interpretation
        ↓
AI generates songs
        ↓
Spotify validates songs
        ↓
Spotify playlist
```

The application is therefore both a **mood interpretation system** and a **music recommendation system**.

---

# 2. Primary Objective

The primary objective is to determine whether structured emotional context can be used to reliably transform a natural-language description of a user's mood into an appropriate Spotify playlist.

The system should answer:

> **Can an AI agent infer a user's emotional state, validate that interpretation with the user, and use the resulting context to generate a useful Spotify playlist?**

---

# 3. User Experience

The intended interaction is conversational.

### Step 1 — User describes their mood

Example:

> "I feel like I have a ton of energy today. I want to get out, do something, and I'm unusually optimistic."

The user does not need to know anything about the mood taxonomy.

### Step 2 — AI interprets the mood

The agent might respond:

> I would describe that as:
>
> **Intensity:** 8/10
> **Core emotion:** Joy
> **Branch:** Excited
> **Specific emotion:** Energetic
>
> You seem highly energized, optimistic, and motivated to act.

### Step 3 — User verifies

The system asks:

> Does that accurately describe how you're feeling?

The user can:

* Confirm.
* Correct the interpretation.
* Provide additional information.

### Step 4 — Playlist generation

Once confirmed:

```text
Verified Mood
    ↓
Recommendation Context
    ↓
Song Candidates
    ↓
Spotify Verification
    ↓
Playlist
```

---

# 4. Core Design Principle

The user is the authority on their own emotional state.

The AI may **infer** the mood, but it must not treat its inference as ground truth.

Therefore:

```text
AI Interpretation ≠ User State

AI Interpretation
        ↓
User Verification
        ↓
Verified Mood Context
```

The verified interpretation becomes the authoritative context for playlist generation.

This creates an explicit human-in-the-loop validation boundary.

---

# 5. Mood Model

The application uses the mood taxonomy defined in **Context System Design v0.1**.

## Intensity

The AI estimates the user's emotional energy on a 1–10 scale.

```text
1–2   Crisis / Exhausted
3–4   Low / Uncomfortable
5–6   Neutral / Baseline
7–8   Positive / Stable
9–10  Peak State
```

The scale represents **emotional intensity/energy**, not a universal measure of emotional health or happiness.

For example:

* A person can be intensely angry.
* A person can be intensely sad.
* A person can be intensely joyful.

Intensity therefore remains independent of the emotional category.

---

# 6. Emotional Taxonomy

The taxonomy provides the vocabulary the AI uses to interpret the user's description.

```text
Joy
├── Content
│   ├── Peaceful
│   └── Satisfied
├── Happy
│   ├── Blissful
│   └── Pleased
└── Excited
    ├── Energetic
    └── Enthusiastic

Sadness
├── Lonely
│   ├── Isolated
│   └── Abandoned
├── Vulnerable
│   ├── Fragile
│   └── Insecure
└── Sluggish
    ├── Heavy
    └── Tired

Anger
├── Irritated
│   ├── Annoyed
│   └── Frustrated
├── Resentful
│   ├── Envious
│   └── Bitter
└── Furious
    ├── Enraged
    └── Hostile

Fear
├── Anxious
│   ├── Overwhelmed
│   └── Worried
├── Scared
│   ├── Terrified
│   └── Helpless
└── Insecure
    ├── Inadequate
    └── Inferior

Disgust
├── Repelled
│   ├── Horrified
│   └── Nauseated
└── Disapproving
    ├── Judgmental
    └── Disappointed

Surprise
├── Amazed
│   ├── Astonished
│   └── Awed
└── Confused
    ├── Disoriented
    └── Perplexed
```

This taxonomy is **context for the agent**, not something the user is required to interact with directly.

---

# 7. Mood Interpretation

Mood interpretation is the first AI reasoning stage.

The agent receives:

```text
User's natural-language description
+
Mood taxonomy
+
Intensity scale
```

It produces a structured interpretation.

Example:

```json
{
  "intensity": 8,
  "core_emotion": "Joy",
  "branch": "Excited",
  "specific_emotion": "Energetic",
  "confidence": 0.87,
  "reasoning_summary": "The user describes unusually high energy, optimism, and motivation to act."
}
```

The internal representation should remain structured even if the user-facing experience is conversational.

---

# 8. Ambiguity Handling

The agent should not be forced to produce a single classification when the user's description is ambiguous.

For example:

```text
Possible interpretation:

1. Joy → Excited → Energetic
2. Joy → Happy → Pleased
```

If the distinction materially affects the playlist, the agent should ask the user to resolve the ambiguity.

The system should therefore support:

```text
Clear interpretation
        ↓
User verification

Ambiguous interpretation
        ↓
Present alternatives
        ↓
User clarification
        ↓
Verified interpretation
```

The system should avoid false precision.

---

# 9. Mood Verification

The interpreted mood must be presented to the user before playlist generation.

The user should be able to:

### Confirm

```text
Yes, that's accurate.
```

### Correct

```text
I'm energetic, but I'm not really happy.
```

### Clarify

```text
I'm excited because I'm nervous about something.
```

The agent then updates the mood representation.

The corrected interpretation becomes the new context.

---

# 10. Context Lifecycle

This application should explicitly demonstrate the Context System Design lifecycle.

```text
Context Generation
        ↓
User describes mood
        ↓
Context Discovery
        ↓
AI identifies emotional signals
        ↓
Context Modeling
        ↓
AI maps signals to taxonomy
        ↓
Context Validation
        ↓
User verifies interpretation
        ↓
Context Assembly
        ↓
Build recommendation context
        ↓
AI Reasoning
        ↓
Generate song candidates
        ↓
External Validation
        ↓
Verify tracks with Spotify
        ↓
Context Delivery
        ↓
Create playlist
        ↓
Evaluation
        ↓
Assess playlist quality
        ↓
Context Evolution
```

The application should make these stages visible in the architecture even if some stages are implemented simply.

---

# 11. Recommendation Generation

After mood verification, the agent generates song candidates.

The agent should receive the **verified mood**, not the original unverified user statement alone.

Example:

```json
{
  "intensity": 8,
  "core_emotion": "Joy",
  "branch": "Excited",
  "specific_emotion": "Energetic"
}
```

The agent should generate more songs than ultimately required.

For example:

```text
Required: 10 songs

Generate: 20–30 candidates
        ↓
Spotify verification
        ↓
Filtering
        ↓
Final 10 songs
```

This reduces the impact of bad recommendations or Spotify search failures.

---

# 12. Recommendation Criteria

The agent should evaluate candidates against the verified mood.

Criteria may include:

* Emotional fit
* Energy level
* Musical character
* Lyrical character
* Genre compatibility
* Artist diversity
* Repetition
* Overall playlist coherence

The exact weighting of these criteria should remain configurable.

The initial implementation should avoid overengineering the scoring system.

---

# 13. Spotify as External Context

Spotify should be treated as the authoritative source for whether a recommended track exists and can be added to the playlist.

The system should distinguish:

```text
AI-generated recommendation
        ≠
Verified Spotify track
```

The workflow is:

```text
Song title + artist
        ↓
Spotify search
        ↓
Track resolution
        ↓
Verified Spotify track URI
```

If a candidate cannot be reliably resolved, it should not be inserted into the playlist.

---

# 14. Playlist Generation

Once the final songs have been validated:

```text
Create Spotify playlist
        ↓
Add verified tracks
        ↓
Return playlist
```

The playlist name should reflect the verified mood.

For example:

> **Joy — Excited — Energetic**

The application may eventually allow the agent to generate more natural playlist names, but structured naming should be used initially because it makes evaluation easier.

---

# 15. Traceability

The system should maintain a traceable relationship between:

```text
User Input
    ↓
AI Interpretation
    ↓
User Verification
    ↓
Recommendation Context
    ↓
Candidate Songs
    ↓
Spotify Validation
    ↓
Final Playlist
```

A run should conceptually produce a record such as:

```json
{
  "user_input": "I feel like I have a ton of energy today...",
  "mood_interpretation": {
    "intensity": 8,
    "core_emotion": "Joy",
    "branch": "Excited",
    "specific_emotion": "Energetic"
  },
  "user_verified": true,
  "candidates_generated": 25,
  "candidates_verified": 22,
  "tracks_selected": 10,
  "playlist_created": true
}
```

This makes the system explainable and allows failures to be investigated.

---

# 16. Failure Modes

The system should explicitly account for several types of failure.

## Interpretation failure

The AI misunderstands the user's mood.

**Resolution:** User correction.

## Taxonomy failure

The user's emotion does not fit cleanly into the current taxonomy.

**Resolution:** Allow the agent to report that no strong match exists rather than forcing a classification.

## Recommendation failure

The songs don't actually fit the verified mood.

**Resolution:** Evaluate and potentially regenerate candidates.

## Spotify resolution failure

A recommended track cannot be reliably found.

**Resolution:** Reject the candidate and use another.

## Playlist coherence failure

The individual songs fit but don't work well together.

**Resolution:** Regenerate or reorder the playlist.

---

# 17. Agent Responsibilities

The AI agent should:

* Read the Context System Design framework.
* Read this design document.
* Understand the mood taxonomy.
* Interpret natural-language mood descriptions.
* Identify ambiguity.
* Generate structured mood representations.
* Request user verification.
* Generate candidate songs.
* Explain recommendation decisions when useful.
* Produce structured data for deterministic components.
* Participate in evaluation.
* Identify missing context.
* Identify contradictions in requirements.
* Document significant design decisions.

The agent should **not** perform deterministic tasks that should be handled by application code.

For example:

```text
Agent:
"September by Earth, Wind & Fire fits the mood."

Application:
"Search Spotify."

Application:
"Resolve track."

Application:
"Create playlist."

Application:
"Add track URI."
```

---

# 18. Context Responsibilities

The system should distinguish between different types of context.

### Domain context

The mood taxonomy and intensity scale.

### User context

The user's current natural-language mood description.

### Derived context

The AI's interpretation of the user's mood.

### Verified context

The interpretation confirmed or corrected by the user.

### Recommendation context

The information supplied to the song-selection stage.

### External context

Spotify's catalog and track metadata.

This distinction is important because these sources have different levels of authority.

---

# 19. Authority Model

The system should establish an explicit hierarchy of authority.

```text
User
  │
  │ authoritative regarding personal emotional state
  ↓
Verified Mood
  │
  │ authoritative recommendation context
  ↓
AI
  │
  │ generates candidate recommendations
  ↓
Spotify
  │
  │ authoritative regarding Spotify catalog
  ↓
Verified Tracks
```

The AI is therefore **not the authority over either the user's feelings or Spotify's catalog**.

It is the reasoning component that connects those systems.

---

# 20. Initial Architecture

The first implementation should remain intentionally small.

```text
                    ┌─────────────────┐
                    │      User       │
                    │ Natural Language│
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │   Mood Agent    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Mood Structure  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ User Validation │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │Recommendation   │
                    │     Agent       │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Song Candidates │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Spotify Search  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Track Validation│
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Spotify Playlist│
                    └─────────────────┘
```

The mood interpretation and recommendation stages may use the same underlying LLM initially. They should nevertheless remain **conceptually separate responsibilities**.

---

# 21. Project Artifacts

The AI coding agent should determine the precise implementation structure.

Potential artifacts include:

```text
Project
│
├── Context System Design reference
├── Application design document
├── Agent instructions
├── Mood taxonomy
├── Mood model/schema
├── Mood interpretation logic
├── Recommendation logic
├── Spotify integration
├── Track validation
├── Configuration
├── Tests
├── Evaluation data
└── Documentation
```

The agent should create only artifacts that are justified by the implementation.

---

# 22. No Premature Infrastructure

The application should not introduce:

* Vector databases
* RAG
* Knowledge graphs
* Complex databases
* Microservices
* Event streaming
* Multi-agent orchestration
* Persistent memory

unless implementation demonstrates a concrete requirement for them.

The initial application should preferably be a small local application.

This directly follows the Context System Design principle:

> **Prefer existing solutions.**

The purpose is to understand the context requirements before introducing architectural complexity.

---

# 23. Evaluation

The system should evaluate both **interpretation** and **playlist quality**.

### Mood Interpretation

Was the AI's classification accepted by the user?

```text
Interpretation accepted
Interpretation corrected
Interpretation ambiguous
```

### Recommendation Quality

How many generated songs were judged appropriate?

### Spotify Resolution

```text
Candidates generated: 25
Spotify matches: 22
Final tracks: 10
```

### Playlist Quality

Does the final playlist:

* Match the mood?
* Match the intensity?
* Feel coherent?
* Contain sufficient variety?
* Avoid obvious mismatches?

---

# 24. Context System Design Experiment

The application should eventually allow comparison between different context strategies.

### Experiment A — Minimal context

```text
User:
"I feel energetic today."

LLM:
Generate playlist.
```

### Experiment B — Structured context

```text
User:
"I feel energetic today."

AI:
Joy → Excited → Energetic
Intensity: 8

User:
Confirmed.

AI:
Generate playlist using verified mood context.
```

The comparison can determine whether the additional context produces a measurably better result.

This turns the application into a **reference implementation and experiment for Context System Design**, rather than simply an AI-powered Spotify utility.

---

# 25. Success Criteria

Version 0.2 is successful if:

1. The user can describe their mood naturally.
2. The AI can map the description onto the mood taxonomy.
3. The AI can estimate intensity.
4. The AI can recognize ambiguity.
5. The user can verify or correct the interpretation.
6. The verified mood becomes the recommendation context.
7. The AI can generate candidate songs.
8. Songs can be verified against Spotify.
9. A Spotify playlist can be created automatically.
10. The system maintains traceability from mood description to playlist.
11. The implementation remains relatively small and understandable.
12. The implementation demonstrates the Context System Design lifecycle.
13. The resulting system generates enough observable information to evaluate whether structured context improves recommendation quality.

---

# 26. Central Design Hypothesis

The central hypothesis is:

> **An AI system that explicitly discovers, models, and validates a user's emotional context will produce more relevant and explainable music recommendations than an AI system that receives only an unstructured mood description.**

The Spotify playlist is the observable output.

The deeper experiment is:

```text
Natural-language input
        ↓
Context discovery
        ↓
Context modeling
        ↓
Human validation
        ↓
Context assembly
        ↓
AI reasoning
        ↓
External validation
        ↓
Observable output
