# Task 004 — Add Application Configuration

Read and follow:

* `AGENTS.md`
* `frameworks/context-system-design-v0.1.md`
* `designs/Mood-Based Spotify Playlist Generator.md`

Review the current implementation before making changes.

## Objective

Move user-configurable application settings out of the source code and into a dedicated configuration file.

The immediate requirement is to make the **number of songs requested by the recommendation prompt configurable**.

## Configuration

Create an appropriate configuration file in a sensible location within the project.

The configuration should contain the number of songs to request.

For example:

```text
song_count: 10
```

Use an appropriate machine-readable format and follow the project's existing conventions.

The exact file format and location should be determined by the agent based on the existing project structure. Do not introduce a configuration framework or external dependency unless necessary.

## Requirements

The application must:

1. Load the song count from the configuration.
2. Use that value when generating the recommendation prompt.
3. Remove the hard-coded song count from application logic.
4. Validate the configuration appropriately.
5. Provide a sensible failure if the configuration is missing or invalid.
6. Keep configuration separate from application logic.
7. Make the configuration easy for a user to find and modify.

For example, changing:

```text
song_count: 10
```

to:

```text
song_count: 20
```

should cause the generated prompt to request 20 songs without requiring any source-code changes.

## Future Configuration

Design the configuration structure so additional application settings can be added later.

Do **not** invent or implement unnecessary configuration options now.

The configuration should simply establish a clean location and mechanism for future settings.

## Prompt Generation

The static recommendation prompt should use the configured value dynamically.

If the configured value is `20`, the generated prompt should say:

```text
Generate 20 songs based on the following mood profile.
```

If it is `10`, it should say:

```text
Generate 10 songs based on the following mood profile.
```

The rest of the prompt behavior should remain unchanged.

## Testing

Add or update tests to verify:

* The configuration loads correctly.
* The configured song count is used in the generated prompt.
* Changing the configured value changes the generated prompt.
* Invalid configuration values are handled appropriately.

All existing tests should continue to pass.

## Cleanup

Remove the existing hard-coded song count from the application wherever it is no longer necessary.

Do not introduce unnecessary abstraction merely to support this single configuration value.

## Documentation

Update `README.md` or other relevant documentation to identify where application configuration is stored and explain how to change the song count.

## Completion Criteria

The task is complete when a user can change the number of requested songs by editing the configuration file without modifying application source code, and the generated prompt reflects the configured value.
