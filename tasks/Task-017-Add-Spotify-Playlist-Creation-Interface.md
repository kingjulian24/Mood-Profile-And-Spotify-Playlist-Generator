## Task 017 — Add Spotify Playlist Creation Interface

### Objective

Extend the React GUI so that, after song recommendations have been successfully imported and validated, the user can create a Spotify playlist directly from the GUI.

This task should connect the existing GUI workflow to the existing backend Spotify integration. Do not reimplement Spotify logic in React.

### Current Workflow

```text
1. Select Mood
       ↓
2. Generate Mood Profile
       ↓
3. Generate Recommendation Prompt
       ↓
4. Paste Chatbot Response
       ↓
5. Parse & Validate Songs
       ↓
6. Review Imported Songs
       ↓
7. Create Spotify Playlist        ← Task 017
       ↓
8. Display Playlist Result
```

---

## Requirements

### 1. Add a Spotify Playlist section

After the validated song recommendations, display a new section for playlist creation.

The section should clearly communicate:

* Number of validated song recommendations
* The current Mood Profile
* The playlist name that will be generated
* A **Create Spotify Playlist** button

Example:

```text
CREATE SPOTIFY PLAYLIST

Mood:
Joy → Happy → Blissful

Songs:
10 validated recommendations

Playlist Name:
Joy — Happy — Blissful — Aug 23, 2026 11:47 PM

[ Create Spotify Playlist ]
```

The displayed playlist name should come from the backend or use the same authoritative backend naming logic used during actual creation. Do not create a separate playlist naming implementation in React.

---

### 2. Use the existing Spotify backend integration

The React frontend must not:

* Authenticate directly with Spotify
* Access Spotify credentials
* Call Spotify APIs directly
* Resolve Spotify track IDs
* Generate Spotify playlist IDs

Instead:

```text
React GUI
    │
    │ HTTP
    ▼
Python Backend
    │
    ▼
SpotifyClient
    │
    ▼
Spotify Web API
```

The backend remains the sole authority for Spotify integration.

---

### 3. Resolve tracks before playlist creation

The application should use the existing backend workflow to resolve the imported song recommendations against Spotify.

The GUI should show progress or status for this process.

For example:

```text
Resolving songs with Spotify...

✓ 8 songs resolved
⚠ 2 songs could not be found
```

The user should be able to see:

* Resolved tracks
* Unresolved tracks
* The reason a track could not be resolved, when available

Do not silently discard unresolved recommendations.

---

### 4. Handle partial resolution

Playlist creation should still be possible when some tracks cannot be resolved, provided at least one track is successfully resolved.

For example:

```text
10 recommendations imported
       ↓
8 resolved on Spotify
       ↓
2 unresolved
       ↓
Create playlist with 8 tracks
```

If zero tracks are resolved, playlist creation must not proceed.

Display a clear error explaining why.

---

### 5. Authentication status and errors

Handle Spotify authentication failures cleanly.

Examples:

* Missing environment credentials
* Expired authorization
* Invalid access token
* Authorization failure
* Spotify API errors

The GUI must display actionable user-facing messages without exposing:

* Client secrets
* Access tokens
* Refresh tokens
* Raw backend stack traces

The frontend must never receive credential values.

---

### 6. Playlist creation result

After successful creation, display:

* Success status
* Playlist name
* Number of tracks added
* Spotify playlist link, when returned by Spotify

Example:

```text
✓ PLAYLIST CREATED

Joy — Happy — Blissful — Aug 23, 2026 11:47 PM

8 tracks added successfully.

[ Open in Spotify ]
```

The Spotify link should open the returned playlist URL.

---

### 7. Prevent duplicate creation

After a successful playlist creation, prevent accidental duplicate submissions.

The interface should not allow repeated clicks to create multiple identical playlists unintentionally.

At minimum:

* Disable the creation button while the request is running.
* Disable or replace the button after successful creation.
* Clearly indicate that the playlist has already been created.

Because playlist names include date and time, duplicate submissions could otherwise create multiple playlists with nearly identical names.

---

### 8. Preserve workflow state

The application should maintain a clear dependency chain:

```text
Mood Selection
      ↓
Mood Profile
      ↓
Recommendation Prompt
      ↓
Imported Recommendations
      ↓
Validated Songs
      ↓
Spotify Resolution
      ↓
Playlist Creation
```

Changing an upstream mood selection must invalidate downstream data.

Changing or replacing the imported song response must invalidate:

* Previous Spotify resolution results
* Previous playlist creation state

The application must not allow a playlist created from stale recommendations to appear associated with a new Mood Profile.

---

## API Requirements

Inspect the existing API endpoints and Spotify integration before adding new backend code.

Reuse existing functionality wherever possible.

If the GUI requires an endpoint that does not currently exist, add the minimum necessary API layer around the existing Python Spotify logic.

Potential responsibilities may include:

```text
POST /api/spotify/resolve
    → Accept validated song recommendations
    → Resolve tracks against Spotify
    → Return resolved and unresolved results

POST /api/spotify/playlists
    → Accept Mood Profile + resolved tracks
    → Create playlist
    → Add resolved tracks
    → Return playlist result
```

These endpoint names are illustrative. The agent should inspect the existing API design and maintain consistency with it.

Do not duplicate Spotify logic already implemented in `src/spotify.py`.

---

## Frontend Structure

The agent may add appropriately scoped components, for example:

```text
frontend/src/components/
├── MoodSelection.jsx
├── MoodProfileView.jsx
├── RecommendationPrompt.jsx
├── SongImport.jsx
└── SpotifyPlaylist.jsx
```

Avoid unnecessary abstraction.

The primary goal is a clear linear workflow.

---

## Error Handling

Handle at least the following scenarios:

| Scenario                      | Expected Behavior                   |
| ----------------------------- | ----------------------------------- |
| No imported songs             | Playlist controls unavailable       |
| No Spotify credentials        | Clear setup/authentication message  |
| Authentication fails          | Display actionable error            |
| Track not found               | Display as unresolved               |
| Some tracks not found         | Allow playlist with resolved tracks |
| Zero tracks resolved          | Prevent playlist creation           |
| Spotify API failure           | Display safe error                  |
| Playlist successfully created | Show success and playlist URL       |
| Duplicate click               | Prevent duplicate playlist creation |

---

## Testing

Add or update tests for:

### Backend

* Track resolution API behavior
* Partial resolution
* Zero-track resolution
* Playlist creation success
* Spotify authentication errors
* Safe API error responses

### Frontend

Where the current test setup supports it, verify:

* Create button is unavailable before valid songs exist
* Resolution status is displayed
* Partial resolution is displayed correctly
* Playlist creation state prevents duplicate submissions
* Successful playlist result is rendered

Run:

```bash
python3 -m unittest discover -s tests
```

And:

```bash
cd frontend
npm run build
```

All existing tests must continue to pass.

---

## Documentation

Update `README.md` to reflect the complete GUI workflow.

Update `AGENTS.md` if this task changes or clarifies project-wide architectural rules.

The documentation should explicitly preserve this authority boundary:

```text
External Chatbot
    → Generates song recommendations

Application
    → Parses recommendations
    → Resolves tracks

Spotify
    → Authoritative source for track availability
    → Creates and stores the playlist
```

## Cleanup

Remove or refactor obsolete GUI placeholders related to Spotify playlist creation.

Do not introduce Spotify credentials, secrets, OAuth tokens, or Spotify Web API calls into the React frontend.
