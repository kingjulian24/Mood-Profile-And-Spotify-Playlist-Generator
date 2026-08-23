# Task 009 — Debug Spotify Authentication and Playlist Creation

## Objective

Debug the current Spotify integration to determine why the application can resolve Spotify tracks but fails during track resolution and playlist creation with authentication-related errors.

Current observed errors include:

```text
Spotify API error (400): Invalid authorization code
````

and:

```text
Spotify API error (403): Forbidden
```

The goal is to identify the root cause before making architectural or functional changes.

## Instructions

Read the existing project documentation, including:

* `AGENTS.md`
* `README.md`
* `designs/`
* `frameworks/`
* `context/`
* Relevant existing source code and tests

Inspect the complete Spotify authentication, token management, track resolution, and playlist creation flow.

Do not assume the cause of the errors.

Specifically investigate:

1. How Spotify authorization codes are obtained and exchanged.
2. How access tokens and refresh tokens are stored and retrieved.
3. How `.cache-spotify.json` is handled.
4. Whether expired or invalid access tokens are detected and refreshed.
5. Whether a newly authorized account can accidentally use an older cached token.
6. Whether track resolution and playlist creation use the same authenticated client/token.
7. Whether the requested OAuth scopes are actually being granted and preserved.
8. Whether the authenticated Spotify user can be identified through the Spotify `/me` endpoint.
9. Whether the application is correctly handling Spotify API error responses.
10. Whether the current implementation can distinguish authentication failures, authorization failures, catalog lookup failures, and playlist creation failures.
11. Whether the current Spotify Development Mode requirements could affect the observed behavior.
12. Whether any existing implementation contains hardcoded credentials, default credentials, or other authentication assumptions.

## Debugging Requirements

Before making changes, determine the most likely root cause based on the actual implementation.

Make the minimum changes necessary to expose useful diagnostic information.

The application should be able to identify the currently authenticated Spotify user during debugging, including at minimum:

* Spotify user ID
* Display name, when available

Do not expose client secrets, access tokens, refresh tokens, or other credentials in output or logs.

If the Spotify API provides a useful error response body, preserve and expose the relevant non-sensitive diagnostic information rather than reducing every failure to a generic status message.

## Scope

This task is for **debugging and correcting the existing implementation only**.

Do not:

* Add new playlist features.
* Change playlist naming.
* Redesign the application architecture.
* Add a callback server unless the investigation determines that it is necessary.
* Introduce new external libraries unless required.
* Change the application's mood-selection workflow.
* Change the recommendation prompt.
* Add unnecessary infrastructure.

Preserve the existing application design wherever possible.

## Testing

Add or update tests necessary to verify any fixes.

At minimum, verify:

* Authentication configuration is correctly loaded.
* Cached credentials are handled correctly.
* Authentication failures are distinguishable from Spotify catalog failures.
* Playlist creation uses the authenticated user/token.
* Spotify API errors provide useful diagnostic information without exposing secrets.
* Existing functionality continues to pass.

Run the complete test suite after making changes.

## Documentation

If the investigation results in an architectural or operational change, update the relevant documentation, including `README.md` and/or `AGENTS.md`.

Do not modify documentation merely to describe implementation details that do not represent a meaningful project decision.

## Completion Criteria

Task 009 is complete when:

1. The root cause of the current `400` and/or `403` errors has been identified.
2. The minimum required fix has been implemented.
3. The application can clearly identify the Spotify account associated with the active authorization during debugging.
4. Authentication/token failures provide actionable diagnostics.
5. No credentials or tokens are exposed.
6. All automated tests pass.
7. The application is ready for another real-world playlist creation test.


