For Task 016, I would move from **documenting the architecture** to making the GUI capable of completing the next actual user step.

## Task 016 — Add Chatbot Response Import Interface

### Objective

Extend the React GUI so that, after generating and displaying the recommendation prompt, the user can paste the external chatbot's response back into the application.

The application should parse the response using the existing backend song-parsing logic and display the parsed song recommendations before any Spotify actions are performed.

### Requirements

#### 1. Add a Chatbot Response Import section

After the Recommendation Prompt section, provide a clear area for the user to paste the chatbot's response.

The interface should include:

* A multiline text area
* A clear label explaining what to paste
* An Import / Parse Songs button
* A visible indication of the expected configured format

For example:

```text
Paste Chatbot Response

Expected format: JSON

[                                      ]
[                                      ]
[                                      ]

              [ Parse Songs ]
```

The frontend must obtain the expected format from the existing application configuration or backend API. Do not hardcode `JSON` in React.

---

#### 2. Use the existing backend parser

Do not implement CSV, JSON, YAML, or other parsing logic in JavaScript.

The React frontend must send the pasted response to the existing backend parsing endpoint.

The Python backend and existing `song_parser` logic remain the authoritative implementation for:

* Format detection/configuration
* Parsing
* Validation
* Required fields
* Error reporting

---

#### 3. Display parsed recommendations

When parsing succeeds, display the parsed songs in a clear list or table.

Each recommendation should show:

* Position
* Song title
* Artist

For example:

```text
Imported Recommendations

  #    Title                    Artist
  ───────────────────────────────────────
  1    Don't Stop Me Now        Queen
  2    Levitating               Dua Lipa
  3    Uptown Funk              Mark Ronson
```

The display should use the structured result returned by the backend rather than reparsing the original text in the frontend.

---

#### 4. Handle parsing errors

If the chatbot response cannot be parsed, display a clear error message.

Examples include:

* Invalid JSON
* Invalid CSV
* Invalid YAML
* Missing required fields
* Empty response
* Invalid song objects

The user must be able to correct the pasted response and try again without restarting the entire workflow.

Do not expose raw Python stack traces to the user.

---

#### 5. Preserve workflow state

The GUI should preserve the current:

* Mood Profile
* Generated recommendation prompt
* Imported response

Changing the mood selection should invalidate downstream results where appropriate.

For example:

```text
Mood changed
    ↓
Previous Mood Profile invalidated
    ↓
Previous Prompt invalidated
    ↓
Previously imported songs invalidated
```

The application should not allow songs generated for one mood profile to silently remain attached to a newly selected mood profile.

---

#### 6. Add clear workflow progression

The GUI workflow should now represent:

```text
1. Select Mood
       ↓
2. Generate Mood Profile
       ↓
3. Generate Recommendation Prompt
       ↓
4. Send Prompt to External Chatbot
       ↓
5. Paste Chatbot Response
       ↓
6. Parse Recommendations
       ↓
7. Review Songs
       ↓
8. Spotify Playlist Creation
```

Spotify playlist creation does not need to be implemented in the GUI as part of this task unless it is already required to support the existing API contract.

The focus of Task 016 is **importing, parsing, and displaying the recommendations**.

---

### API Requirements

Inspect the existing backend API before making changes.

If an appropriate song parsing endpoint already exists, use it.

If the endpoint exists but is incomplete for GUI use, update it minimally.

Do not create a second parsing implementation or duplicate existing application logic.

The API response should provide structured song data suitable for direct rendering by the React frontend.

---

### Frontend Components

The agent may introduce appropriately scoped components, such as:

```text
components/
├── MoodSelection.jsx
├── MoodProfileView.jsx
├── RecommendationPrompt.jsx
└── SongImport.jsx
```

This structure is illustrative, not mandatory.

Avoid unnecessary component fragmentation.

---

### Testing

Add or update tests for:

* Successful import of the configured response format
* Invalid response handling
* Missing `title`
* Missing `artist`
* Empty response
* Correct structured results returned to the frontend
* State invalidation when the mood changes

Run:

```bash
python3 -m unittest discover -s tests
```

Also verify:

```bash
cd frontend
npm run build
```

All existing tests must continue to pass.

---

### Documentation

Update:

* `README.md`
* `AGENTS.md`, if this task changes or clarifies project-wide architectural guidance

Document that:

> The external chatbot generates recommendations. The application does not trust the raw response as application data until it has been parsed and validated by the backend.

### Cleanup

Remove or refactor any code made obsolete by the new GUI import workflow.

Do not duplicate song parsing or validation logic between Python and React.
