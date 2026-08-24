# Task 020 — Debug GUI Spotify OAuth Flow

## Objective

Debug the Spotify OAuth flow introduced in Task 019.

The GUI currently displays a "Connect Spotify" button. Clicking it opens Spotify authentication successfully, and the user can authorize the application.

However, after authorization, the GUI does not transition to an authenticated state.

The Python server console instead prompts:

    Enter redirect URL or code:

This indicates that the existing manual OAuth authentication flow is still being invoked somewhere in the GUI authentication path.

The goal of this task is to identify and fix the integration so that GUI authentication is completely automatic.

---

## Expected GUI OAuth Flow

The intended flow is:

    User clicks "Connect Spotify"
            ↓
    React calls /api/spotify/auth/start
            ↓
    Backend creates authorization URL
            ↓
    Browser opens Spotify
            ↓
    User authorizes application
            ↓
    Spotify redirects to registered callback
            ↓
    Python callback server receives authorization code
            ↓
    Backend exchanges code for tokens
            ↓
    Tokens are cached
            ↓
    Backend retrieves Spotify /me profile
            ↓
    GUI detects authenticated state
            ↓
    GUI displays connected Spotify account

At no point in this flow should the application ask:

    Enter redirect URL or code:

---

## Investigation Requirements

Trace the entire authentication path.

Inspect at minimum:

- `src/spotify.py`
- `src/server.py`
- `frontend/src/App.jsx`
- `frontend/src/api/client.js`
- Spotify authentication-related tests

Identify:

1. Where `/api/spotify/auth/start` begins authentication.
2. Where the callback server is started.
3. Where the callback receives the authorization code.
4. Where the code is exchanged for tokens.
5. Whether the callback invokes `SpotifyClient.authenticate()`.
6. Whether `SpotifyClient.authenticate()` still invokes the legacy `input()`-based authentication flow.
7. How the GUI determines that authentication has completed.
8. Whether the authentication state is correctly propagated back to the GUI.

Do not assume the Task 019 implementation is correct merely because the tests pass.

---

## Architectural Requirement

Separate the two authentication mechanisms clearly.

### GUI Authentication

The GUI flow must use:

    authorization URL
        ↓
    local callback server
        ↓
    authorization code
        ↓
    token exchange
        ↓
    token cache

It must NOT use terminal input.

### CLI Authentication

The existing CLI may continue to support:

    Enter redirect URL or code:

if that remains useful.

Do not unnecessarily remove the CLI authentication workflow.

The two flows should share the underlying token exchange and token-management logic without sharing the interactive input mechanism.

---

## Important Constraint

Do not solve the problem by automatically providing input to the existing `input()` call.

Do not add hacks involving:

- simulated stdin
- fake redirect input
- hardcoded authorization codes
- delays/sleeps
- polling for arbitrary periods
- browser scraping

Fix the authentication architecture so the callback flow directly supplies the authorization code to the token-exchange logic.

---

## Callback Behavior

Verify that the callback server:

1. Receives `/callback?code=...`.
2. Extracts the code.
3. Handles OAuth errors such as:

       /callback?error=access_denied

4. Exchanges the code for tokens.
5. Saves the token cache.
6. Retrieves the authenticated Spotify profile.
7. Signals authentication completion.
8. Returns a useful browser response.

The browser response should clearly indicate success or failure.

---

## Frontend Behavior

After authentication completes:

- Stop authentication polling.
- Refresh Spotify status.
- Display the authenticated Spotify account.
- Do not require a page refresh.
- Do not require terminal interaction.

If authentication fails:

- Stop polling.
- Display an understandable error.
- Allow the user to try again.

---

## Multiple Spotify Accounts

Continue using the Spotify `/me` response as the authoritative identity.

After successful authentication, verify that the GUI displays the account actually authorized through Spotify.

Do not infer the account from:

- Spotify Developer Dashboard account
- client ID
- environment variables
- cached display names

---

## Token Cache

Verify that successful GUI authentication creates/updates:

    .cache-spotify.json

Verify that subsequent application starts can use the cache without requiring OAuth again.

Do not expose token contents to React.

---

## Testing

Add or update tests covering the actual GUI OAuth backend flow.

At minimum test:

- `/api/spotify/auth/start`
- callback with valid authorization code
- callback with OAuth error
- callback with missing code
- token exchange
- token cache creation
- authenticated status after callback
- confirmation that GUI authentication never calls `input()`

Mock Spotify HTTP requests.

Do not use real Spotify credentials.

---

## Manual Verification

After implementation, perform the following real-world test:

1. Delete/rename the existing Spotify token cache.
2. Start the Python backend.
3. Start the React frontend.
4. Open the GUI.
5. Confirm Spotify shows "Not Connected".
6. Click "Connect Spotify".
7. Authenticate with the desired Spotify account.
8. Authorize the application.
9. Allow Spotify to redirect to localhost.
10. Confirm the terminal does NOT ask for:

       Enter redirect URL or code:

11. Confirm the browser displays a successful authentication message.
12. Return to the GUI.
13. Confirm the GUI automatically displays the authenticated Spotify account.
14. Create a playlist.
15. Confirm the playlist is created in the authenticated account.
16. Restart the application.
17. Confirm the cached token authenticates automatically.

---

## Verification

Run:

    python3 -m unittest discover -s tests

and:

    npm run build

Both must pass.

The final implementation must support both:

    CLI → manual OAuth authentication

and:

    GUI → automatic browser OAuth authentication

without the two flows interfering with each other.