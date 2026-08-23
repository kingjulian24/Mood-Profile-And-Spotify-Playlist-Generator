# Task 005 — Make Recommendation Output Format Configurable

Read and follow:

* `AGENTS.md`
* `frameworks/context-system-design-v0.1.md`
* `designs/Mood-Based Spotify Playlist Generator.md`
* The current application configuration
* The current prompt-generation implementation

## Objective

Update the recommendation prompt so that the external chatbot returns song recommendations in a **machine-readable format** suitable for the next stage of the application.

The application itself still does not communicate with an LLM or Spotify.

The workflow is:

```text
Mood Profile
    ↓
Prompt Generator
    ↓
External Chatbot
    ↓
Machine-Readable Song List
    ↓
[Future Task: Import & Spotify Playlist]
```

## Output Format Configuration

Add a new configurable application setting that determines the requested recommendation output format.

The format should be configurable independently of the application code.

Initially support:

* `json`
* `csv`
* `yaml`

For example:

```json
{
  "song_count": 10,
  "output_format": "json"
}
```

Changing the value to:

```json
{
  "song_count": 10,
  "output_format": "csv"
}
```

must cause the generated prompt to request CSV instead.

Use the existing configuration system from Task 004.

Validate the configured format and provide a clear error for unsupported values.

Do not add unnecessary configuration infrastructure.

## Prompt Template

Update the static recommendation prompt so that it explicitly tells the external chatbot:

1. How many songs to generate.
2. That the recommendations must be based on the supplied mood profile.
3. Which fields are required for each song.
4. Which machine-readable format to use.
5. That the response should contain only the requested structured data, without explanatory prose.

At minimum, each recommendation must contain:

* `title`
* `artist`

The prompt should make the output contract explicit.

For example, when configured for JSON, the generated prompt should communicate an expected structure equivalent to:

```json
{
  "songs": [
    {
      "title": "Song Title",
      "artist": "Artist Name"
    }
  ]
}
```

When configured for CSV, the prompt should request an equivalent structure with:

```text
title,artist
Song Title,Artist Name
```

When configured for YAML, the prompt should request an equivalent structured representation.

The exact wording of the prompt should be determined by the implementation, but the requirements above must be unambiguous.

## Important Constraint

The application must **not parse, validate, or process the chatbot's response yet**.

This task only changes what the generated prompt asks the external chatbot to produce.

The next stage will consume the resulting song list programmatically.

## Testing

Add or update tests covering:

* Valid output-format configuration.
* Unsupported output format.
* Prompt generation for JSON.
* Prompt generation for CSV.
* Prompt generation for YAML.
* Correct song count in each generated prompt.
* Required `title` and `artist` fields being specified.
* Prompt output containing no ambiguity about the requested response format.

All existing tests must continue to pass.

## Documentation

Update `README.md` and any other relevant documentation to explain:

* The configurable `output_format`.
* The currently supported formats.
* The purpose of the machine-readable output.
* That the application does not yet consume the generated song list.

Do not implement Spotify integration or song-list importing as part of this task.

## Cleanup

Review the existing prompt-generation code while making this change.

Remove any obsolete wording or assumptions that conflict with the new machine-readable output requirement.

Do not introduce functionality that belongs to the next stage of the project.

## Completion Criteria

The task is complete when:

1. The output format can be changed through `config.json`.
2. The supported formats are validated.
3. The generated prompt explicitly requests the configured format.
4. The generated prompt specifies `title` and `artist` as required song data.
5. The prompt requests only structured song data from the external chatbot.
6. No LLM or external service is called by the application.
7. All tests pass.
8. Documentation reflects the new configuration and output contract.
