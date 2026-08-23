# Mood Profile & Spotify Playlist Generator

A reference implementation demonstrating **Context System Design (v0.1)**.

---

## Overview

The **Mood Profile & Spotify Playlist Generator** creates personalized Spotify playlists by combining structured human emotional context with external AI song recommendations:

1. **Deterministic Mood Selection:** Guides the user through the canonical mood taxonomy to determine a structured **Mood Profile** and canonical mood code (e.g. `J-3-1:8`).
2. **Machine-Readable Prompt Generation:** Produces a structured prompt requesting song recommendations in `json`, `csv`, or `yaml` from an external chatbot.
3. **Song List Ingestion:** Accepts and validates the machine-readable song recommendations from the chatbot (via interactive paste or file).
4. **Deterministic Spotify Resolution & Playlist Creation:** Resolves candidate tracks against Spotify's catalog and creates a named Spotify playlist (e.g., `Joy — Excited — Energetic`) populated with all resolved tracks, reporting any unresolved songs clearly.

---

## Context System Design Lifecycle

```text
Context Generation      User selects mood via interactive CLI
        ↓
Context Modeling        Application structures choices into a Mood Profile & code (e.g. J-3-1:8)
        ↓
Prompt Assembly         Static prompt template is populated with Mood Profile & config settings
        ↓
External AI Reasoning   External chatbot produces machine-readable song recommendations (JSON/CSV/YAML)
        ↓
Song Ingestion          Application parses and validates the structured song list
        ↓
External Validation     Application resolves song titles & artists against Spotify Web API
        ↓
Context Delivery        Application creates and populates the Spotify playlist
```

---

## Key Features

* **Authoritative Human Emotion:** The user explicitly chooses their core emotion, branch, specific emotion, and intensity.
* **External AI Bridge:** The application generates strict, machine-readable prompt contracts (`json`, `csv`, `yaml`) for external chatbots.
* **Deterministic Track Resolution:** Searches Spotify using structured track and artist filters with fallback matching, avoiding hallucinated songs.
* **Graceful Partial Failure Handling:** Successfully adds all resolved tracks while clearly listing any songs that could not be matched.
* **Canonical Taxonomy:** Uses [`context/mood-taxonomy.json`](context/mood-taxonomy.json) as the single source of truth.

---

## Configuration & Environment Variables

### Application Settings (`config.json`)
Managed in [`config.json`](config.json) at the root of the project:

```json
{
  "song_count": 10,
  "output_format": "json"
}
```

* `song_count`: Number of songs requested from the chatbot (default: `10`).
* `output_format`: Machine-readable format requested: `"json"`, `"csv"`, or `"yaml"`.

---

## Spotify Credentials & Environment Setup

Spotify credentials are sensitive secrets and are read strictly from **environment variables**. They are never hardcoded or stored in application configuration files.

### Required Environment Variables

| Variable | Required | Description |
| :--- | :--- | :--- |
| `SPOTIFY_CLIENT_ID` | Yes | Client ID from Spotify Developer Dashboard. |
| `SPOTIFY_CLIENT_SECRET` | Yes | Client Secret from Spotify Developer Dashboard. |
| `SPOTIFY_REDIRECT_URI` | Optional | Redirect URI (default: `http://127.0.0.1:8888/callback`). |
| `SPOTIFY_ACCESS_TOKEN` | Optional | Direct OAuth access token override (bypasses auth flow). |

### How to Obtain Spotify Credentials
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and log in.
2. Click **Create an App**.
3. Set **App Name** to `Mood Playlist Generator` (or any name).
4. Add `http://127.0.0.1:8888/callback` under **Redirect URIs** in your app settings.
5. Copy your **Client ID** and **Client Secret**.

### Configuring the Local Environment

A safe template [`set-spotify-env.example.sh`](set-spotify-env.example.sh) is provided in the repository.

1. Copy the example template to create your local script:
   ```bash
   cp set-spotify-env.example.sh set-spotify-env.sh
   ```

2. Edit `set-spotify-env.sh` and fill in your Client ID and Client Secret:
   ```bash
   export SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
   export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
   export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
   ```

3. **Source** the script in your terminal before running the application:
   ```bash
   source ./set-spotify-env.sh
   ```

> **Security Note:** `set-spotify-env.sh` is excluded by [`.gitignore`](.gitignore) and will never be committed to Git.

---

## Usage

### 1. Interactive CLI Mode (Full End-to-End Workflow)
```bash
# 1. Source your environment variables
source ./set-spotify-env.sh

# 2. Run the application
python3 main.py
```

Workflow:
1. Select Core Emotion, Branch, Specific Emotion, and Intensity.
2. Review the Mood Profile and confirm to generate the chatbot prompt.
3. Copy and submit the prompt to your chatbot (ChatGPT, Claude, Gemini, etc.).
4. Choose `[I]mport` and paste the chatbot's structured response (or path to a saved file).
5. The application resolves each track on Spotify, creates the playlist, and outputs the Spotify URL.

### 2. Direct Command-Line & File Import
Generate a playlist directly from a mood code and a saved song list file:
```bash
python3 main.py --code J-3-1:8 --import-songs path/to/songs.json
```

### 3. Prompt Only / Code Validation
Generate a prompt without interactive prompts:
```bash
python3 main.py --code J-3-1:8
```

Output mood profile as JSON:
```bash
python3 main.py --code J-3-1:8 --json
```

### 4. Display Full Taxonomy
```bash
python3 main.py --dump-taxonomy
```

### 5. Run Automated Tests
```bash
python3 -m unittest discover -s tests
```

---

## Project Structure

```text
.
├── AGENTS.md                  # Operating guidelines for AI coding agents
├── README.md                  # Project overview and usage documentation
├── config.json                # User application configuration (song_count, output_format)
├── set-spotify-env.example.sh # Safe template for Spotify API credentials
├── set-spotify-env.sh         # Local credentials script (ignored by Git)
├── main.py                    # Root entrypoint
├── src/                       # Application source code
│   ├── __init__.py
│   ├── config.py              # Configuration loader and validator
│   ├── models.py              # MoodProfile, SongRecommendation, ResolvedTrack models
│   ├── taxonomy.py            # Taxonomy traversal, validation, and code parsing
│   ├── prompt.py              # Machine-readable prompt templates (JSON, CSV, YAML)
│   ├── song_parser.py         # Ingestion and validation for JSON, CSV, and YAML song lists
│   ├── spotify.py             # Spotify authentication, search resolution, and playlist creation
│   ├── mood_selection.py      # Interactive CLI wizard and import coordinator
│   └── cli.py                 # CLI argument parsing
├── tests/                     # Automated unit test suite
│   ├── __init__.py
│   ├── test_config.py         # Configuration tests
│   ├── test_taxonomy.py       # Taxonomy and code parsing tests
│   ├── test_prompt.py         # Prompt template rendering tests
│   ├── test_song_parser.py    # Song list parsing and validation tests
│   ├── test_spotify.py        # Spotify API and track resolution mock tests
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
    ├── Task-003—Simplify-Application-to-Mood-Profile-Prompt-Generator.md
    ├── Task-004-Add-Application-Configuration.md
    ├── Task-005-Make-Recommendation-Output-Format-Configurable.md
    ├── Task-006-Import-Song-List-and-Create-Spotify-Playlist.md
    └── Task-007-Add-Credentials-to-Environment.md
```
