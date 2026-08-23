# Task 010 — Fix Spotify Playlist Items Endpoint Tests

## Objective

The Spotify playlist item endpoint was manually updated from:

POST /v1/playlists/{playlist_id}/tracks

to:

POST /v1/playlists/{playlist_id}/items

The application code has already been updated. Some existing tests are now failing because they still expect the previous endpoint.

Update the test suite and any affected test fixtures or mocks so that the tests correctly reflect the current Spotify API endpoint.

Use the existing project design, framework, and application architecture as the source of truth.

Do not make unrelated changes.

Run the complete test suite and ensure all tests pass.