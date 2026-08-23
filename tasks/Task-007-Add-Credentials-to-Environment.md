# Task 007 — Add Credentials to Environment

Read and follow:

* `AGENTS.md`
* `README.md`
* The current Spotify integration
* The current configuration system
* The existing Git configuration

## Objective

Configure the application to obtain Spotify authentication credentials from environment variables rather than hardcoded values or application configuration files.

The credentials are secrets and must remain local to the developer's environment.

## Requirements

### 1. Environment Variable Support

Update the Spotify authentication implementation so that it reads the required Spotify credentials from environment variables.

Inspect the existing Spotify implementation to determine the exact variables required.

Do not hardcode credentials anywhere in the source code.

The application should provide a clear error when required credentials are unavailable.

### 2. Local Credential Setup Script

Create a local Bash script that allows the developer to configure the required Spotify environment variables conveniently.

The script should:

* Contain placeholder locations for the required credentials.
* Export the credentials as environment variables.
* Be designed to be **sourced** into the current shell rather than executed as a subprocess.

For example:

```bash
source ./set-spotify-env.sh
```

After sourcing the script, the application should be able to access the credentials through the environment.

The exact script name and location should be determined by the existing project structure.

### 3. Protect Credentials from Git

The local credential script contains secrets and must never be committed.

Add the script to `.gitignore`.

Review `.gitignore` for any other credential or authentication artifacts created by the existing Spotify implementation and ensure they are also excluded where appropriate.

Do not remove existing security protections.

### 4. Credential Template

Because the actual credential script will be ignored by Git, provide a safe template or documentation showing the required environment variables without containing real credentials.

For example:

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

The template must contain placeholders only.

### 5. Authentication Behavior

Do not redesign the Spotify authentication flow as part of this task.

Preserve the existing authentication behavior and modify only how credentials are supplied to it.

The application should continue to support the authentication mechanism already implemented in Task 006.

## Security Requirements

Credentials must never:

* Be hardcoded in source code.
* Be committed to Git.
* Appear in tests.
* Appear in logs.
* Appear in normal CLI output.
* Be included in documentation.
* Be stored in `config.json`.

Review the repository for accidental credential exposure while completing the task.

## Testing

Add or update tests to verify:

* Credentials are read from environment variables.
* Missing credentials produce a clear error.
* Credentials are not hardcoded.
* Existing Spotify functionality remains unaffected.

Tests must not require real Spotify credentials.

## Documentation

Update `README.md` to explain:

1. Which environment variables are required.
2. How to obtain the Spotify credentials.
3. How to configure the local environment.
4. How to source the local credential script.
5. That the credential script is intentionally ignored by Git.

Do not document or include real credentials.

## Scope

This task is only concerned with credential/environment configuration.

Do not add:

* Playlist naming configuration.
* New Spotify functionality.
* New application configuration settings.
* LLM integration.
* Changes to the mood-selection workflow.

## Completion Criteria

The task is complete when:

1. Spotify credentials are supplied through environment variables.
2. A local Bash script can be sourced to configure those variables.
3. The credential script is ignored by Git.
4. A safe credential template or equivalent documentation exists.
5. No credentials are hardcoded or exposed.
6. Missing credentials produce a clear error.
7. Existing tests pass.
8. Existing Spotify functionality continues to work.
