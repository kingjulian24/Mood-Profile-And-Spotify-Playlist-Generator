# Task 006 — Import Song List and Create Spotify Playlist

Read and follow:

* `AGENTS.md`
* `frameworks/context-system-design-v0.1.md`
* `designs/Mood-Based Spotify Playlist Generator.md`
* `README.md`
* The current application configuration
* The current prompt-generation implementation
* The current machine-readable recommendation output requirements

## Objective

Extend the application so that it can take the machine-readable song recommendations produced by the external chatbot and use them to create a Spotify playlist.

The application should now extend the workflow to:

```text
Mood Selection
      ↓
Mood Profile
      ↓
Recommendation Prompt
      ↓
External Chatbot
      ↓
Song List
      ↓
Application
      ↓
Spotify Track Resolution
      ↓
Spotify Playlist
```

The external chatbot remains outside the application.

The application must not generate or interpret song recommendations using an LLM.

## Input

The application should accept a song list produced by the external chatbot according to the output format established in Task 005.

The implementation should support the configured machine-readable format(s) already established by the project.

The agent should determine the most appropriate way to accept this input based on the existing project structure and conventions.

Do not require the user to manually convert the chatbot's output into another format if the existing configured format can be consumed directly.

## Song Data

At minimum, each song recommendation contains:

* `title`
* `artist`

The application should parse the input and extract these values.

The application should validate the input before attempting Spotify operations.

Malformed or incomplete recommendations should be handled clearly rather than causing an unexplained failure.

## Spotify Integration

Implement the Spotify integration required to:

1. Authenticate the user appropriately.
2. Search Spotify for each supplied song.
3. Resolve recommendations to Spotify tracks.
4. Handle songs that cannot be resolved.
5. Create a playlist.
6. Add the successfully resolved tracks to the playlist.

Spotify should be treated as the authoritative source for track existence and metadata.

Do not assume that a song supplied by the chatbot exists on Spotify.

## Track Resolution

The application should resolve each recommendation against Spotify using the available song information.

The implementation should account for reasonable search ambiguity.

For example, the chatbot may return a song title and artist that have multiple matches.

The agent should determine an appropriate deterministic resolution strategy.

Do not use an LLM to resolve tracks.

## Playlist

Create a Spotify playlist containing the successfully resolved tracks.

Use the selected mood profile when constructing the playlist name.

For example:

```text
Joy — Excited — Enthusiastic
```

The implementation may determine an appropriate naming convention based on the existing mood profile representation.

The playlist should contain the tracks in the order provided by the recommendation list unless Spotify requires otherwise.

## Failure Handling

The application should handle partial failures gracefully.

For example:

```text
10 recommendations received
8 tracks resolved
2 tracks not found
8 tracks added to playlist
```

A failed Spotify lookup should not necessarily prevent valid recommendations from being added.

The application should clearly report which recommendations could not be resolved.

## Authentication & Security

Determine the appropriate Spotify authentication mechanism based on the current Spotify API requirements and the application's intended local CLI usage.

Do not hardcode:

* Client IDs
* Client secrets
* Access tokens
* Refresh tokens
* Other credentials

Use an appropriate secure configuration mechanism.

Do not commit credentials or generated authentication artifacts to Git.

## Configuration

Inspect the existing configuration system before introducing new configuration.

Add configuration only where it represents a genuine user-configurable behavior.

Do not unnecessarily duplicate or replace the existing configuration mechanism.

If Spotify credentials or settings are required, use an appropriate mechanism consistent with the project's existing security conventions.

## Architecture

Maintain the separation of responsibilities established by the project:

```text
Mood Selection
    ↓
Mood Profile
    ↓
Prompt Generation
    ↓
External Chatbot
    ↓
Song List Import
    ↓
Deterministic Spotify Integration
    ↓
Playlist
```

The application should not contain an LLM.

Spotify operations should remain deterministic and separate from mood selection and prompt generation.

## Testing

Add appropriate tests for the new functionality.

Tests should cover, as appropriate:

* Valid song-list parsing.
* Invalid song-list input.
* Missing required fields.
* Spotify search/resolution behavior.
* Unresolved tracks.
* Partial resolution.
* Playlist naming.
* Playlist creation behavior.

Do not require live Spotify API access for ordinary unit tests.

Use appropriate mocking or test doubles for external Spotify operations.

## Documentation

Update `README.md` and `AGENTS.md` to reflect the new application workflow.

Document:

* How to provide the chatbot-generated song list.
* How Spotify authentication is configured.
* How the playlist is created.
* How unresolved songs are handled.
* Any required setup steps.

Keep the documentation focused on the actual implementation.

## Cleanup

Review the existing code while implementing this task.

Remove or simplify obsolete code where appropriate.

Do not preserve unnecessary abstractions simply because they were introduced in earlier tasks.

## Completion Criteria

The task is complete when a user can:

1. Run the application.
2. Generate a mood profile and recommendation prompt.
3. Submit the prompt to an external chatbot.
4. Provide the resulting machine-readable song list to the application.
5. Authenticate with Spotify.
6. Have the application resolve the songs against Spotify.
7. Have the application create a Spotify playlist containing the successfully resolved tracks.
8. Clearly see any recommendations that could not be resolved.

The application must perform all Spotify operations deterministically and must not require an LLM.
