## Task 014 — Add Recommendation Prompt Interface


### Objective

Extend the React GUI so that, after the user generates and confirms a Mood Profile, the application displays the recommendation prompt generated from that profile.

The prompt should use the existing configurable application settings, including `song_count` and the configured response format.

### Requirements

1. **Add a Recommendation Prompt view**

   * Display the generated prompt after the Mood Profile is created.
   * Keep the Mood Profile visible so the user can see the context used to generate the prompt.

2. **Use the existing backend**

   * Do not duplicate prompt-generation logic in React.
   * The frontend should call the existing `/api/prompt` endpoint.
   * The Python backend remains responsible for constructing the prompt.

3. **Display the complete generated prompt**

   * Include the configured number of songs.
   * Include the complete Mood Profile:

     * Intensity
     * Core Emotion
     * Branch
     * Specific Emotion
     * Mood Code
   * Include the configured machine-readable response format and required fields.

4. **Make the prompt easy to copy**

   * Provide a **Copy Prompt** button.
   * Use the browser clipboard API.
   * Give the user clear visual feedback when copying succeeds.

5. **Add workflow navigation**

   * Provide a way to return to the Mood Profile/mood-selection step.
   * Returning should not corrupt the existing taxonomy state.

6. **Preserve the existing architecture**

   * React handles presentation and interaction.
   * Python handles domain logic and prompt generation.
   * Do not introduce another prompt template or hardcoded song count in JavaScript.

7. **Testing**

   * Add/update frontend tests where the existing project setup supports them.
   * Add/update Python API tests for `/api/prompt` if necessary.
   * Verify that changing `song_count` or response format in `config.json` is reflected in the GUI-generated prompt.
   * Run the complete existing test suite and ensure all tests pass.

### Cleanup

Remove or refactor any GUI code introduced in previous tasks that duplicates backend prompt-generation behavior. There should be **one authoritative implementation of prompt construction**.

### Documentation

Update:

* `README.md`
* `AGENTS.md`

Document the new GUI workflow and reinforce that prompt generation remains a backend responsibility.

The agent should update `AGENTS.md` whenever this task introduces or changes an architectural rule, workflow boundary, configuration responsibility, or other project-wide operating guidance.
