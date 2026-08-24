# Task 019 — Add GUI Spotify Authentication

## Objective

Add a complete Spotify OAuth authentication flow to the React GUI so that users can connect their Spotify account directly from the application.

The current application requires manual OAuth handling when no cached Spotify authentication exists. Replace that manual workflow with a GUI-driven authentication flow while preserving the existing backend authentication architecture.

The user should be able to:

1. Open the GUI.
2. See whether Spotify is authenticated.
3. Click "Connect Spotify" when unauthenticated.
4. Authenticate through Spotify in the browser.
5. Return to the application automatically.
6. See which Spotify account is connected.
7. Continue to playlist creation without manually copying authorization codes.

---

## Current Architecture

Preserve the existing architecture:

```text
React GUI
    |
    | HTTP API
    v
Python API Server
    |
    +-- Spotify Client
            |
            +-- OAuth
            +-- Token Cache
            +-- Spotify Web API
````

React must never receive or store:

* Spotify client secret
* access token
* refresh token

All Spotify credentials and token management remain in Python.

---

## Requirements

### 1. Add GUI Authentication Controls

When Spotify is not authenticated, display:

```text
Spotify
Not Connected

[ Connect Spotify ]
```

When authenticated, display:

```text
Spotify
Connected as <display name>

[ Disconnect ]   (if supported)
```

The existing authenticated user information should be reused where possible.

---

### 2. Add Backend OAuth Start Endpoint

Create an API endpoint such as:

```text
GET /api/spotify/auth/start
```

The endpoint should:

1. Verify that required Spotify application credentials are available.
2. Generate the Spotify authorization URL.
3. Return the authorization URL to the frontend.

Do not expose the Spotify client secret.

The authorization request must include the scopes required by the application, including playlist creation and the existing user-profile scope.

---

### 3. Add Local OAuth Callback Handling

Implement a local callback mechanism compatible with the registered Spotify redirect URI.

For example:

```text
http://127.0.0.1:8888/callback
```

The backend must:

1. Receive the authorization callback.
2. Extract the authorization code.
3. Exchange the code for Spotify access and refresh tokens.
4. Store the tokens using the existing cache mechanism.
5. Retrieve the authenticated Spotify profile.
6. Make the authenticated state available to the GUI.

The authorization code must remain a backend concern.

Do not send the authorization code to React.

---

### 4. Browser Flow

The intended flow is:

```text
User clicks "Connect Spotify"
        |
        v
React requests /api/spotify/auth/start
        |
        v
Backend returns Spotify authorization URL
        |
        v
Browser opens Spotify
        |
        v
User authenticates / authorizes
        |
        v
Spotify redirects to local callback
        |
        v
Python backend exchanges code for tokens
        |
        v
Token cache created/updated
        |
        v
Spotify profile retrieved
        |
        v
GUI reflects authenticated state
```

Use the simplest reliable local implementation.

The Python standard library may be used for the callback server if appropriate.

Do not introduce a large OAuth framework unless there is a clear technical reason.

---

### 5. Multiple Spotify Accounts

The application must make it clear which Spotify account has been authenticated.

After authentication, retrieve the current Spotify user profile and display at minimum:

* display name, when available
* Spotify user ID

Example:

```text
Spotify Connected

Account: Jim
User ID: abc123
```

This is important because the user may have multiple Spotify accounts.

The application must never assume that the Spotify Developer account and the Spotify account being used for playlist creation are necessarily the same identity.

The authenticated Spotify `/me` response is the authoritative source for the active user.

---

### 6. Existing Token Cache

Preserve the existing token cache behavior.

If a valid cached token exists:

```text
Application starts
        ↓
Valid cache
        ↓
Automatically authenticated
```

The GUI should display the authenticated account without requiring another authorization flow.

If the cached token is expired but a refresh token is available, use the existing refresh mechanism.

Only initiate interactive authorization when the application cannot authenticate using the existing cache.

---

### 7. Authentication Status Endpoint

Provide an endpoint such as:

```text
GET /api/spotify/status
```

It should return a safe representation of authentication state.

For example:

```json
{
  "authenticated": true,
  "display_name": "Jim",
  "user_id": "abc123"
}
```

When unauthenticated:

```json
{
  "authenticated": false
}
```

Do not return:

* access tokens
* refresh tokens
* client secrets
* authorization codes

---

### 8. Frontend Authentication State

The React application should periodically or explicitly refresh Spotify authentication status.

At minimum:

* Check status when the application loads.
* Update status after the OAuth flow completes.
* Update the interface without requiring the user to restart the application.

Do not require the user to manually refresh the page.

---

### 9. OAuth Completion Page

After Spotify redirects to the callback, provide a simple browser response.

For example:

```text
Spotify Connected

Authentication was successful.

You can return to the Mood Playlist Generator.
```

If authentication fails:

```text
Spotify Authentication Failed

We could not connect your Spotify account.

You can close this window and try again.
```

Do not expose credentials, authorization codes, or internal stack traces.

---

### 10. Error Handling

Handle at minimum:

* Missing Spotify client credentials
* User denies authorization
* Invalid/expired authorization code
* Callback missing authorization code
* OAuth token exchange failure
* Callback server unavailable
* Redirect URI mismatch
* Spotify API authentication failure
* Expired cached token
* Invalid cached token

Errors should be understandable to the user and should identify the appropriate recovery action.

---

### 11. Preserve Existing Playlist Creation

Do not change the existing playlist creation behavior except where necessary to use the new authentication flow.

After authentication, this existing workflow must continue to work:

```text
Mood Profile
    ↓
Prompt
    ↓
Chatbot Response
    ↓
Song Validation
    ↓
Spotify Resolution
    ↓
Create Playlist
```

The playlist must be created for the Spotify account shown as authenticated in the GUI.

---

### 12. Security Requirements

Never expose the following to the React application:

```text
SPOTIFY_CLIENT_SECRET
SPOTIFY_ACCESS_TOKEN
SPOTIFY_REFRESH_TOKEN
OAuth authorization code
```

Never commit credentials or token cache files.

Continue honoring the existing `.gitignore` configuration.

---

### 13. Testing

Add/update automated tests for:

* unauthenticated status
* authenticated status
* authorization URL generation
* missing credentials
* successful OAuth callback
* OAuth error callback
* token exchange
* token cache creation
* cached authentication
* token refresh
* Spotify user identity retrieval
* authentication status API
* playlist creation after GUI authentication

All Spotify network interactions must be mocked.

Tests must not require real Spotify credentials.

---

## Cleanup

As part of this task, remove or simplify any obsolete manual OAuth workflow that is no longer necessary for normal GUI usage.

The CLI may retain manual authentication support if it remains useful.

Do not remove working CLI authentication unless there is a clear reason.

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

Manually verify:

```text
Start application
    ↓
Spotify shows "Not Connected"
    ↓
Click "Connect Spotify"
    ↓
Spotify authorization page opens
    ↓
Authorize correct Spotify account
    ↓
Spotify redirects to local callback
    ↓
Authentication succeeds
    ↓
GUI shows connected account
    ↓
Generate mood
    ↓
Import songs
    ↓
Resolve songs
    ↓
Create playlist
    ↓
Verify playlist appears in the authenticated Spotify account

