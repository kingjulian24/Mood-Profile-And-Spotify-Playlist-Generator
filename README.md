# Mood Profile & Spotify Playlist Generator

A reference implementation demonstrating **Context System Design (v0.1)**.

---

## Overview

The **Mood Profile & Spotify Playlist Generator** creates personalized Spotify playlists by combining structured human emotional context with external AI song recommendations:

1. **Deterministic Mood Selection:** Guides the user through the canonical mood taxonomy to determine a structured **Mood Profile** and canonical mood code (e.g. `J-3-1:8`).
2. **Machine-Readable Prompt Generation:** Produces a structured prompt requesting song recommendations in `json`, `csv`, or `yaml` from an external chatbot.
3. **Song List Ingestion:** Accepts and validates the machine-readable song recommendations from the chatbot (via interactive paste or file).
4. **Deterministic Spotify Resolution & Playlist Creation:** Resolves candidate tracks against Spotify's catalog and creates a named Spotify playlist (e.g., `Joy — Excited — Energetic — Aug 23, 2026 3:42 PM`) populated with all resolved tracks, reporting any unresolved songs clearly.

The application provides two complementary user interfaces sharing the exact same Python business logic:
- **Web Graphical User Interface (React + Vite)**: A modern, dark-themed visual presentation layer.
- **Interactive Command-Line Interface (CLI)**: A lightweight terminal-based workflow.

---

## Context System Design Lifecycle

```text
Context Generation      User selects mood via React GUI or interactive CLI
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
* **Dual Presentation Interfaces:** Clean React GUI and deterministic interactive CLI running on top of a shared Python domain model.
* **External AI Bridge:** The application generates strict, machine-readable prompt contracts (`json`, `csv`, `yaml`) for external chatbots.
* **Deterministic Track Resolution:** Searches Spotify using structured track and artist filters with fallback matching, avoiding hallucinated songs.
* **Graceful Partial Failure Handling:** Successfully adds all resolved tracks while clearly listing any songs that could not be matched.
* **Zero Logic Duplication:** The React GUI communicates with the Python backend via a lightweight REST API server, keeping business logic centralized.

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

Spotify credentials are sensitive secrets and are read strictly from **environment variables**. They are never hardcoded or stored in application configuration files or exposed to the frontend.

### Required Environment Variables

| Variable | Required | Description |
| :--- | :--- | :--- |
| `SPOTIFY_CLIENT_ID` | Yes | Client ID from Spotify Developer Dashboard. |
| `SPOTIFY_CLIENT_SECRET` | Yes | Client Secret from Spotify Developer Dashboard. |
| `SPOTIFY_REDIRECT_URI` | Optional | Redirect URI (default: `http://127.0.0.1:8888/callback`). |
| `SPOTIFY_ACCESS_TOKEN` | Optional | Direct OAuth access token override (bypasses auth flow). |

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

3. **Source** the script in your terminal:
   ```bash
   source ./set-spotify-env.sh
   ```

---

## Usage

### 1. Graphical User Interface (React Web App)

The React GUI runs locally and communicates with the Python backend API:

```bash
# Terminal 1: Start the Python Backend API Server
source ./set-spotify-env.sh
python3 main.py --serve

# Terminal 2: Start the React Frontend
cd frontend
npm run dev
```

Open your browser at `http://localhost:3000`.

---

### 2. Interactive CLI Mode
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

---

### 3. Direct Command-Line & File Import
Generate a playlist directly from a mood code and a saved song list file:
```bash
python3 main.py --code J-3-1:8 --import-songs path/to/songs.json
```

---

### 4. Display Full Taxonomy
```bash
python3 main.py --dump-taxonomy
```

---

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
├── main.py                    # Root entrypoint (CLI and --serve backend)
├── frontend/                  # React + Vite Graphical User Interface
│   ├── package.json           # Frontend dependencies
│   ├── vite.config.js         # Vite configuration with API proxy
│   ├── index.html             # HTML entrypoint
│   └── src/
│       ├── main.jsx           # React DOM root
│       ├── App.jsx            # Application shell & workflow sections
│       ├── index.css          # Dark theme design system tokens & styles
│       └── api/
│           └── client.js      # Backend REST API client
├── src/                       # Python core application source code
│   ├── __init__.py
│   ├── config.py              # Configuration loader and validator
│   ├── models.py              # MoodProfile, SongRecommendation, ResolvedTrack models
│   ├── taxonomy.py            # Taxonomy traversal, validation, and code parsing
│   ├── prompt.py              # Machine-readable prompt templates (JSON, CSV, YAML)
│   ├── song_parser.py         # Ingestion and validation for JSON, CSV, and YAML song lists
│   ├── spotify.py             # Spotify authentication, search resolution, and playlist creation
│   ├── server.py              # HTTP REST API server for GUI communication
│   ├── mood_selection.py      # Interactive CLI wizard and import coordinator
│   └── cli.py                 # CLI argument parsing
├── tests/                     # Automated unit test suite
│   ├── __init__.py
│   ├── test_config.py         # Configuration tests
│   ├── test_taxonomy.py       # Taxonomy and code parsing tests
│   ├── test_prompt.py         # Prompt template rendering tests
│   ├── test_song_parser.py    # Song list parsing and validation tests
│   ├── test_spotify.py        # Spotify API and track resolution mock tests
│   ├── test_server.py         # Backend REST API endpoint tests
│   └── test_mood_selection.py # Interactive CLI flow tests
├── context/                   # Canonical domain context and schemas
│   ├── mood-taxonomy.json     # Canonical mood taxonomy and intensity scales
│   └── schemas/
│       └── mood-selection.json# JSON schema for MoodProfile
├── frameworks/                # Context System Design framework
│   └── context-system-design-v0.1.md
├── designs/                   # Architecture and UI design documents
│   ├── Mood-Based Spotify Playlist Generator.md
│   └── Mood-Based-Spotify-Playlist-Generator-GUI.md
└── tasks/                     # Task specifications
```
