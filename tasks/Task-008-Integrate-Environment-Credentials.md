# Task 008 — Integrate Environment Credentials

Read and follow:

* `AGENTS.md`
* `README.md`
* `Task-007-Add-Credentials-to-Environment.md`
* The current Spotify integration
* The current credential/environment setup

## Objective

Ensure the application's Spotify authentication code actually uses the environment variables established in Task 007.

Task 007 established the credential-management mechanism. This task integrates that mechanism into the application's Python code.

## Requirements

Inspect the existing Spotify authentication implementation and identify every location where Spotify credentials are currently obtained.

Replace any hardcoded credential values or assumptions with environment-based credential loading.

The application must obtain Spotify credentials from the environment variables established in Task 007:

* `SPOTIFY_CLIENT_ID`
* `SPOTIFY_CLIENT_SECRET`
* `SPOTIFY_REDIRECT_URI`
* `SPOTIFY_ACCESS_TOKEN` when supported by the existing authentication flow

Do not hardcode credential values in Python source code.

## Authentication

The existing Spotify authentication behavior should remain intact.

Only change the source of the credentials.

The application should:

1. Read the required values from the environment.
2. Validate that required credentials are present.
3. Produce a clear error when required credentials are missing.
4. Pass the credentials into the existing Spotify authentication mechanism.
5. Continue to support the authentication flow implemented in Task 006.

Do not create a second authentication system.

## Credential Precedence

Inspect the existing implementation and establish a clear precedence rule if multiple credential sources currently exist.

Environment variables should be the authoritative source for Spotify credentials.

Do not silently fall back to hardcoded credentials.

If another credential mechanism exists for compatibility, document its relationship to environment variables rather than allowing ambiguous behavior.

## Security

Search the repository for:

* Spotify client IDs
* Spotify client secrets
* Access tokens
* Hardcoded redirect URIs where they should be configurable

Remove any actual secret values from source code.

Do not expose credentials through:

* Logs
* Exceptions
* CLI output
* Tests
* Documentation

Do not modify the user's local credential script or expose its contents.

## Testing

Update the existing Spotify tests to verify the actual integration boundary.

Tests should demonstrate that:

* `SPOTIFY_CLIENT_ID` is read from the environment.
* `SPOTIFY_CLIENT_SECRET` is read from the environment.
* `SPOTIFY_REDIRECT_URI` is read from the environment.
* `SPOTIFY_ACCESS_TOKEN`, when used, is read from the environment.
* Missing required credentials produce the expected error.
* The Spotify authentication layer receives the environment-provided values.
* No hardcoded credentials are required.

Use mocked values in tests.

Tests must never use real Spotify credentials or make real Spotify API calls.

Run the complete test suite after the change.

## Documentation

Review `README.md` and ensure its instructions accurately describe how the application obtains Spotify credentials.

The documentation should describe the actual implementation rather than merely describing the credential setup scripts.

If the existing documentation makes claims that are no longer accurate, correct them.

## Cleanup

Review the Spotify authentication code for obsolete credential-handling logic.

Remove redundant or conflicting credential sources where appropriate.

Do not refactor unrelated Spotify functionality.

## Scope

This task is specifically about connecting the existing environment credential mechanism to the Python application.

Do not implement:

* Playlist naming.
* New Spotify API functionality.
* New recommendation functionality.
* Changes to mood selection.
* Changes to prompt generation.

## Completion Criteria

The task is complete when:

1. The Python application obtains Spotify credentials from environment variables.
2. No Spotify credentials are hardcoded in Python source.
3. The existing Spotify authentication flow uses those environment-provided credentials.
4. Missing credentials fail clearly.
5. Tests verify the actual environment-to-authentication integration.
6. No real credentials are used in tests.
7. All tests pass.
8. Documentation accurately describes the implemented behavior.
