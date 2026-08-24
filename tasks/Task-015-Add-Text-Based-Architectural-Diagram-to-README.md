## Task 015 — Add Text-Based Architectural Diagram to README

### Objective

Add a clear text-based architectural diagram to `README.md` that visually represents the current architecture of the Mood-Based Spotify Playlist Generator.

The diagram should help a reader understand the major application components, how they communicate, and where the boundaries between the frontend, backend, application logic, external chatbot, and Spotify exist.

### Requirements

#### 1. Add an Architecture section to README

Add a dedicated section such as:

```markdown
## Architecture
```

Place the architecture section in a logical location within the existing README.

#### 2. Create a text-based architecture diagram

Use an ASCII or Unicode text diagram inside a Markdown code block.

The diagram should reflect the application's current architecture, including:

* React GUI
* CLI
* Python API Server
* Shared Python application/domain logic
* Mood taxonomy
* Configuration
* Prompt generation
* External chatbot
* Song recommendation import/parsing
* Spotify API
* Spotify playlist creation

The diagram should clearly show that both the GUI and CLI interact with the same underlying Python application logic.

A conceptual structure might look similar to:

```text
                         USER
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
        React GUI                       CLI
              │                         │
              │ HTTP                    │ Direct Python Calls
              ▼                         ▼
        Python API Server               │
              │                         │
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────────┐
              │   Shared Application Logic  │
              │                             │
              │  • Mood Selection           │
              │  • Taxonomy Traversal       │
              │  • Mood Profile             │
              │  • Prompt Generation        │
              │  • Song Parsing             │
              │  • Spotify Integration      │
              └──────────────┬──────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Mood Taxonomy     Config       Environment
        mood-taxonomy     config.json  Spotify Credentials
              │              │              │
              └──────────────┴──────────────┘
                             │
                             ▼
                     Recommendation Prompt
                             │
                             ▼
                      External Chatbot
                             │
                             ▼
                    JSON / CSV / YAML Songs
                             │
                             ▼
                        Song Parser
                             │
                             ▼
                        Spotify API
                             │
                             ▼
                      Spotify Playlist
```

This is a conceptual example, not necessarily the exact final diagram. The agent should inspect the current implementation and ensure the final diagram accurately represents the actual architecture.

#### 3. Accuracy is more important than appearance

The agent must derive the diagram from the current codebase and documentation.

Do not document planned architecture as if it already exists.

If Task 014 or earlier tasks changed the actual architecture, the diagram must reflect those changes.

#### 4. Show architectural boundaries

The diagram should make the following boundaries understandable:

* **User interface boundary**

  * React GUI
  * CLI

* **Backend boundary**

  * Python API server

* **Shared application logic**

  * Existing deterministic domain/application modules

* **External services**

  * External chatbot
  * Spotify Web API

* **Configuration and secrets**

  * `config.json`
  * Environment variables / local credential setup

#### 5. Preserve architectural principles

The diagram and surrounding documentation should make clear that:

* The application itself does not use an LLM to determine the user's mood.
* Mood selection is deterministic and user-driven.
* Prompt generation is deterministic and template-based.
* The external chatbot is responsible for generating song recommendations.
* The application parses and validates the returned recommendations.
* Spotify is the authority for track resolution and playlist creation.
* Spotify credentials remain on the backend/environment side and are never exposed to the React frontend.

#### 6. Add a brief explanation below the diagram

After the diagram, add a concise explanation of the end-to-end flow:

```text
1. The user selects their mood through the GUI or CLI.
2. The application generates a structured Mood Profile.
3. The application generates a deterministic recommendation prompt.
4. The user sends the prompt to an external chatbot.
5. The chatbot returns song recommendations in the configured format.
6. The recommendations are imported back into the application.
7. The application resolves the songs against Spotify.
8. The application creates and populates the Spotify playlist.
```

Adjust the wording if necessary to match the current implementation exactly.

### Documentation Integrity

Update `AGENTS.md` if the task reveals that the existing architecture documentation or project-wide architectural rules need clarification.

Do not modify application behavior for this task unless a documentation change exposes an actual inconsistency that must be corrected.

### Verification

Before completing the task:

1. Verify that the diagram matches the current codebase.
2. Verify that all component names and file responsibilities are accurate.
3. Ensure the README renders correctly in Markdown.
4. Run the existing test suite to confirm that no unrelated behavior was affected.
5. Report any architectural discrepancy discovered during documentation.
