Yes. At this point, a design document makes more sense than immediately creating tasks. The CLI has established the application behavior; the GUI should be a presentation layer over that existing workflow rather than a redesign of the underlying system.

I would keep the first version deliberately small:

**Mood selection → Mood profile → Recommendation prompt → Song response → Spotify resolution → Playlist → Status**

And importantly, **no LLM inside the application**. The external chatbot remains the recommendation engine.

# Design Document

**Filename:** `Mood-Based-Spotify-Playlist-Generator-GUI.md`

````markdown
# Mood-Based Spotify Playlist Generator — GUI Design

> **Status:** Draft
>
> This document defines the design for a graphical user interface for the
> Mood-Based Spotify Playlist Generator. The GUI is intended to replace the
> existing CLI interaction while preserving the application's existing
> deterministic workflow.

---

# 1. Purpose

The GUI provides a simple graphical interface for generating Spotify
playlists from a user's current mood.

The application does not use an LLM to determine the user's mood or generate
songs.

Instead:

1. The user selects their mood through the application.
2. The application generates a structured mood profile.
3. The application generates a recommendation prompt.
4. The user submits that prompt to an external chatbot.
5. The user pastes the chatbot's machine-readable response back into the
   application.
6. The application resolves the songs against Spotify.
7. The application creates the Spotify playlist.
8. The application displays the result and execution status.

The GUI is therefore a visual interface over the existing application logic,
not a replacement for it.

---

# 2. Design Goals

The GUI should:

- Replace the existing CLI workflow.
- Make mood selection simple and intuitive.
- Clearly display the resulting mood profile.
- Provide a copyable recommendation prompt.
- Accept chatbot-generated song recommendations.
- Validate the imported song data.
- Resolve songs against Spotify.
- Create the Spotify playlist.
- Display progress and errors clearly.
- Preserve the deterministic nature of the existing application.
- Reuse existing application logic wherever practical.

The GUI should not:

- Integrate an LLM.
- Attempt to infer the user's mood.
- Automatically generate songs.
- Introduce unnecessary backend infrastructure.
- Replace the existing mood taxonomy.
- Duplicate business logic that already exists in the Python application.

---

# 3. User Workflow

The primary workflow is:

```text
Select Mood
     ↓
Select Branch
     ↓
Select Specific Emotion
     ↓
Select Intensity
     ↓
View Mood Profile
     ↓
Generate Recommendation Prompt
     ↓
Copy Prompt
     ↓
Use External Chatbot
     ↓
Paste Song Recommendations
     ↓
Validate Song Data
     ↓
Resolve Songs Against Spotify
     ↓
Create Playlist
     ↓
Display Result
````

The GUI should visually represent this progression.

---

# 4. Technology

## Frontend

Use React for the GUI.

The interface should use a modern component-based architecture without
introducing a large UI framework unless one provides a clear benefit.

The initial implementation should prioritize:

* Simplicity
* Maintainability
* Responsive layout
* Accessibility
* Clear state transitions

## Backend

The existing Python application remains responsible for:

* Mood taxonomy
* Mood profile generation
* Prompt generation
* Song parsing
* Spotify authentication
* Spotify track resolution
* Playlist creation

The GUI should call this functionality rather than reimplementing it.

The exact frontend/backend communication mechanism should be determined
during implementation based on the existing project structure.

---

# 5. Visual Design

## Theme

The application should use a dark theme.

The design should feel:

* Modern
* Clean
* Focused
* Minimal
* Slightly polished

Avoid:

* Excessive animation
* Excessive gradients
* Visual clutter
* Large decorative elements
* Unnecessary dashboards

The primary purpose of the interface is to guide the user through the
workflow.

---

# 6. Application Layout

The main interface should consist of a centered application container.

Conceptually:

```text
┌──────────────────────────────────────────────────────────┐
│                                                          │
│       Mood-Based Spotify Playlist Generator             │
│                                                          │
│       Create a playlist from how you feel.               │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. YOUR MOOD                                            │
│                                                          │
│  Core Emotion                                             │
│  [ Joy ▼ ]                                                │
│                                                          │
│  Branch                                                   │
│  [ Happy ▼ ]                                              │
│                                                          │
│  Specific Emotion                                         │
│  [ Blissful ▼ ]                                           │
│                                                          │
│  Intensity                                                │
│  [ 7 ▼ ]                                                  │
│                                                          │
│                     [ Generate Profile ]                  │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  2. MOOD PROFILE                                          │
│                                                          │
│  Joy → Happy → Blissful                                   │
│  Intensity: 7                                             │
│  Mood Code: J-2-1:7                                       │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  3. RECOMMENDATION PROMPT                                 │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Generate 10 songs based on...                       │  │
│  │                                                    │  │
│  │ ...                                                │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│                    [ Copy Prompt ]                        │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  4. SONG RECOMMENDATIONS                                  │
│                                                          │
│  Paste the chatbot response below.                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                    │  │
│  │ {                                                  │  │
│  │   "songs": [...]                                   │  │
│  │ }                                                  │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│                    [ Import Songs ]                        │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  5. SPOTIFY                                               │
│                                                          │
│  10 songs received                                       │
│  10 songs resolved                                       │
│                                                          │
│                    [ Create Playlist ]                    │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  STATUS                                                   │
│                                                          │
│  ✓ Playlist created successfully                         │
│                                                          │
│  Joy — Happy — Blissful — Aug 23, 2026 6:31 PM          │
│                                                          │
│                    [ Open in Spotify ]                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

The actual visual implementation may differ from this wireframe.

---

# 7. Mood Selection

Mood selection should be progressive.

The user should first select:

1. Core emotion
2. Branch
3. Specific emotion
4. Intensity

Each selection should constrain the available options in the following
selection.

For example:

```text
Core Emotion
    ↓
Joy

Branch
    ↓
Happy

Specific Emotion
    ↓
Blissful

Intensity
    ↓
7
```

The GUI should load these values from the canonical mood taxonomy rather than
hardcoding them into React components.

Canonical source:

```text
context/mood-taxonomy.json
```

---

# 8. Mood Profile

After selection, the application displays:

```text
Intensity: 7
Core Emotion: Joy
Branch: Happy
Specific Emotion: Blissful
Mood Code: J-2-1:7
```

The profile should be visually distinct from the selection controls.

The user should be able to change the selections without restarting the
workflow.

---

# 9. Recommendation Prompt

The application generates the recommendation prompt using the existing
prompt template and application configuration.

The prompt should include:

* Configured number of songs
* Mood profile
* Required response format
* Any configured recommendation constraints

Example:

```text
Generate 10 songs based on the following mood profile.

Intensity: 7
Core Emotion: Joy
Branch: Happy
Specific Emotion: Blissful
Mood Code: J-2-1:7

Return the recommendations in JSON format containing an array of objects
under a "songs" key.

Each object must contain exactly the following fields:

- "title": string
- "artist": string
```

The prompt should be displayed in a copyable text area.

The user can copy it and use it with any external chatbot.

---

# 10. Song Import

After obtaining recommendations from an external chatbot, the user pastes
the response into the GUI.

The application should support the configured response format.

The initial supported formats are:

* JSON
* CSV
* YAML

The GUI should provide clear instructions about the expected format.

Example JSON:

```json
{
  "songs": [
    {
      "title": "Good Life",
      "artist": "Kanye West"
    },
    {
      "title": "Golden",
      "artist": "Jill Scott"
    }
  ]
}
```

The application should parse and validate the response before attempting
Spotify operations.

---

# 11. Song Validation

After import, the GUI should display basic validation information.

Example:

```text
Song Recommendations

✓ 10 songs imported
✓ Valid format
✓ Required fields present
```

If validation fails:

```text
Unable to import recommendations.

The following problems were found:

• Song 4 is missing an artist.
• Song 7 contains an invalid JSON structure.
```

The user should be allowed to correct the input and try again.

---

# 12. Spotify Resolution

Once valid songs are imported, the application resolves each song against
Spotify.

The GUI should display progress.

Example:

```text
Resolving songs against Spotify...

████████████████████░░  9 / 10

Resolved: 9
Unresolved: 1
```

After completion:

```text
Resolution Results

✓ Resolved: 9 / 10

Unresolved:
• Example Song — Example Artist
  Reason: No matching Spotify track found.
```

Unresolved tracks should not prevent successfully resolved tracks from being
used unless the application determines that playlist creation cannot
reasonably continue.

---

# 13. Playlist Creation

The application should create the playlist using the existing Spotify
integration.

The playlist name should continue to follow the existing format:

```text
Core Emotion — Branch — Specific Emotion — Date Time
```

Example:

```text
Joy — Happy — Blissful — Aug 23, 2026 6:31 PM
```

The naming logic should remain in the backend/application domain logic.

The frontend should not construct playlist names itself.

---

# 14. Status & Feedback

The GUI should provide clear status feedback throughout the workflow.

Possible states include:

```text
Idle
Selecting Mood
Profile Generated
Prompt Ready
Waiting for Recommendations
Recommendations Imported
Validating Songs
Resolving Spotify Tracks
Creating Playlist
Complete
Error
```

The user should always be able to determine what the application is
currently doing.

Errors should explain:

1. What failed.
2. Why it failed when known.
3. What the user can do next.

---

# 15. Spotify Authentication

Spotify authentication remains an application/backend responsibility.

The GUI should not expose:

* Client ID
* Client Secret
* Access tokens
* Refresh tokens

Credentials remain managed through the existing environment configuration.

The GUI may provide a simple authentication status indicator:

```text
Spotify
✓ Connected as: <Spotify User>
```

or:

```text
Spotify
○ Not connected

[ Connect Spotify ]
```

The exact authentication UX should be determined during implementation
without exposing credentials to the frontend.

---

# 16. Configuration

Existing application configuration should remain centralized.

The GUI should not duplicate configuration values.

For example:

```text
config.json

{
  "song_count": 10,
  "response_format": "json"
}
```

The GUI should consume the application's configuration rather than
maintaining independent frontend configuration.

Future configuration options may be added without redesigning the interface.

---

# 17. Architecture

The intended architecture is:

```text
                    React GUI
                        │
                        ▼
              Application Interface
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
 Mood/Profile Logic              Prompt Generation
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
                User / External LLM
                        │
                        ▼
                  Song Response
                        │
                        ▼
                  Song Parser
                        │
                        ▼
                Spotify Service
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Track Resolution       Playlist Creation
```

The React frontend is responsible for presentation and user interaction.

The Python application remains responsible for domain and integration logic.

---

# 18. Separation of Concerns

## Frontend

Responsible for:

* Rendering UI
* Capturing user selections
* Displaying mood profiles
* Displaying prompts
* Accepting song responses
* Displaying application state
* Triggering backend operations

## Application

Responsible for:

* Taxonomy
* Mood profile generation
* Prompt generation
* Configuration
* Song parsing
* Validation
* Spotify authentication
* Track resolution
* Playlist creation

## External Chatbot

Responsible for:

* Generating song recommendations from the supplied prompt

The external chatbot is not part of the application architecture.

---

# 19. Error Handling

The GUI should handle existing application errors without duplicating their
logic.

Important cases include:

* Invalid mood selection
* Invalid song format
* Missing song fields
* Spotify authentication failure
* Spotify authorization failure
* Track resolution failure
* Playlist creation failure
* Network failure

Errors should be displayed in human-readable form.

---

# 20. Scope of Initial GUI

The first GUI implementation should include only:

1. Mood selection
2. Mood profile display
3. Prompt generation
4. Prompt copying
5. Song response input
6. Song validation
7. Spotify track resolution
8. Playlist creation
9. Status display
10. Spotify authentication status

The first version should not include:

* User accounts
* Persistent application database
* Recommendation history
* Analytics dashboard
* LLM integration
* Social features
* Playlist editing
* Advanced Spotify discovery
* Complex animations

---

# 21. Design Principle

The GUI should be considered a new interface, not a new application.

The existing deterministic application remains the source of truth.

The objective is to make the existing workflow easier to use without
introducing unnecessary complexity.

```text
CLI ───────┐
           │
           ▼
     Application Logic
           ▲
           │
GUI ───────┘
```

The CLI may remain available for development, testing, and automation.

The GUI becomes the primary user interface for normal use.

```

## Tasks I'd create from this

I would **not** make one giant "build GUI" task. I'd break it into a few controlled tasks:

| Task | Purpose |
|---|---|
| **012 — Initialize GUI Architecture** | Set up React/frontend structure and establish the frontend/backend boundary |
| **013 — Implement Mood Selection UI** | Replace the CLI mood-selection interaction with the GUI |
| **014 — Implement Mood Profile & Prompt UI** | Display the profile and provide the copyable prompt |
| **015 — Implement Song Import UI** | Paste/import chatbot response and display validation |
| **016 — Integrate Spotify Workflow** | Connect the GUI to song resolution and playlist creation |
| **017 — Implement Application Status & Error UI** | Give the workflow coherent progress/error states |
| **018 — GUI Polish & Responsive Design** | Dark theme, layout, accessibility, responsive behavior |

I would start with **Task 012**, because there's an architectural question we shouldn't let the agent casually decide while implementing everything else: **how the React frontend communicates with the existing Python application**.

That is the one part I'd explicitly design before handing the implementation over to the agent.
```
