# Task 018 — Complete and Polish End-to-End GUI Workflow

## Objective

Review and refine the React GUI so that the complete workflow operates as one coherent, intuitive application from mood selection through Spotify playlist creation.

The application should guide the user through the existing workflow without requiring them to understand the underlying API, Python backend, taxonomy, or Spotify implementation.

This task is primarily an integration, UX, and consistency task.

Do not introduce new application capabilities unless required to make the existing workflow function correctly.

---

## Current Workflow

The intended workflow is:

1. Select Core Emotion
2. Select Branch
3. Select Specific Emotion
4. Select Intensity
5. Generate Mood Profile
6. Generate Recommendation Prompt
7. Copy prompt into an external chatbot
8. Paste chatbot response into the application
9. Parse and validate song recommendations
10. Resolve songs against Spotify
11. Create Spotify playlist
12. Open the resulting playlist in Spotify

---

## Requirements

### 1. Review the Complete Workflow

Inspect the existing frontend and backend implementation and verify that the complete workflow operates correctly from beginning to end.

Do not assume that because individual components work independently that the overall workflow is correct.

Verify:

- Mood selection produces the correct profile.
- Mood profile produces the correct prompt.
- Prompt reflects the configured song count and output format.
- Chatbot response can be pasted into the application.
- Song data is parsed and validated by the backend.
- Valid songs can be resolved against Spotify.
- Resolved tracks can be sent to playlist creation.
- Playlist creation uses the active authenticated Spotify account.
- The resulting playlist URL is presented to the user.

---

### 2. Improve Workflow Progression

Make the progression through the application visually obvious.

The user should be able to understand:

- where they currently are
- what they have completed
- what they need to do next
- which steps are unavailable until prerequisites are satisfied

Use the existing dark visual design.

Do not introduce unnecessary animations or visual complexity.

---

### 3. Make State Dependencies Explicit

Ensure downstream state is invalidated whenever an upstream value changes.

Examples:

Changing:

- Core Emotion

must invalidate:

- Branch
- Specific Emotion
- Mood Profile
- Prompt
- Imported Songs
- Spotify Resolution
- Playlist Creation

Changing:

- Branch

must invalidate:

- Specific Emotion
- Mood Profile
- Prompt
- Imported Songs
- Spotify Resolution
- Playlist Creation

Changing:

- Specific Emotion
- Intensity

must invalidate:

- Mood Profile
- Prompt
- Imported Songs
- Spotify Resolution
- Playlist Creation

Importing a new song list must invalidate:

- Spotify Resolution
- Playlist Creation

Resolving tracks must not invalidate the imported song list.

---

### 4. Prevent Invalid Actions

Buttons and controls should only be available when their prerequisites are satisfied.

Examples:

- Cannot generate a profile until all mood selections are complete.
- Cannot import songs before a prompt/profile exists.
- Cannot resolve songs before valid songs have been imported.
- Cannot create a playlist until at least one track has been resolved.
- Cannot create the same playlist request multiple times simultaneously.

The backend must remain authoritative for validation.

Do not duplicate business rules unnecessarily in React.

---

### 5. Improve Error Handling

Errors should be presented in a way that helps the user recover.

Handle at minimum:

- Backend unavailable
- Invalid mood selection
- Invalid chatbot response
- Unsupported song format
- Missing title/artist
- Spotify authentication failure
- Spotify track resolution failure
- Spotify playlist creation failure
- Partial track resolution

Do not display Python stack traces or raw HTTP errors to the user.

Where possible, provide a clear next action.

---

### 6. Make Spotify Authentication Status Visible

The GUI should provide a simple indication of whether Spotify is available/authenticated.

Do not expose:

- client secrets
- access tokens
- refresh tokens

The backend must continue to own authentication.

If authentication is unavailable, the GUI should explain that Spotify authentication is required before playlist creation.

---

### 7. Preserve Existing Backend Architecture

Do not move Spotify authentication, taxonomy logic, prompt generation, song parsing, or playlist creation logic into JavaScript.

The architecture should remain:

```text
React GUI
    |
    | HTTP API
    v
Python API Server
    |
    +-- Mood Taxonomy
    +-- Mood Profile
    +-- Prompt Generator
    +-- Song Parser
    +-- Spotify Client
````

React is responsible for presentation and interaction.

Python remains responsible for domain logic and external service integration.

---

### 8. Preserve CLI Functionality

The existing CLI must continue to work.

Do not remove or break:

```bash
python3 main.py
```

or existing CLI/API functionality unless there is a compelling reason.

The GUI is an additional interface to the application, not a replacement for the underlying domain logic.

---

### 9. Verify Configuration Usage

Confirm that the GUI workflow respects existing configuration values rather than hardcoding them.

At minimum verify:

* song count
* song output format

If additional configuration values already exist, verify that they continue to be respected.

---

### 10. Add/Update Tests

Add tests where necessary to verify the end-to-end workflow.

At minimum test:

* successful workflow progression
* invalidation of downstream state
* invalid actions
* successful song import
* partial Spotify resolution
* successful playlist creation
* Spotify errors
* backend unavailable state

Use mocked Spotify/API interactions.

Do not require real Spotify credentials for automated tests.

---

### 11. Update Documentation

Update `README.md` to describe the GUI workflow.

Include:

* how to start the backend
* how to start the frontend
* the workflow from mood selection to playlist creation
* where the external chatbot fits into the workflow
* Spotify authentication requirements

Also update `AGENTS.md` if any architectural or development rules change.

---

## Cleanup

As part of this task, identify and remove:

* dead React components
* unused CSS
* duplicated logic
* obsolete API calls
* obsolete state
* temporary debugging code
* unnecessary dependencies

Do not perform unrelated refactoring.

The goal is a clean, coherent implementation of the existing design.

---

## Verification

Run:

```bash
python3 -m unittest discover -s tests
```

and:

```bash
npm run build
```

Both must pass.

Manually verify the complete workflow:

```text
Select mood
    ↓
Generate profile
    ↓
Generate prompt
    ↓
Copy prompt to chatbot
    ↓
Paste chatbot response
    ↓
Validate songs
    ↓
Resolve against Spotify
    ↓
Create playlist
    ↓
Open playlist
```

The final application should feel like one continuous workflow rather than a collection of separate features.

