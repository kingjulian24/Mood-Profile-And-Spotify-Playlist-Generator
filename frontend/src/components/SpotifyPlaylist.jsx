import React, { useState } from 'react';
import { api } from '../api/client';

export function SpotifyPlaylist({
  profile,
  parsedSongs,
  resolutionResult,
  onResolutionDone,
  playlistResult,
  onPlaylistCreated,
  disabled,
}) {
  const [resolving, setResolving] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  if (disabled || !profile || !parsedSongs || parsedSongs.length === 0) {
    return (
      <div className="empty-spotify-state">
        <p>Complete Steps 1–4 to validate song recommendations before resolving tracks and creating your playlist.</p>
      </div>
    );
  }

  // Handle resolving songs against Spotify catalog
  const handleResolve = async () => {
    setResolving(true);
    setError(null);

    try {
      const result = await api.resolveTracks(parsedSongs);
      onResolutionDone(result);
    } catch (err) {
      setError(err.message || 'Failed to resolve songs on Spotify.');
    } finally {
      setResolving(false);
    }
  };

  // Handle creating Spotify playlist with resolved tracks
  const handleCreatePlaylist = async () => {
    if (!resolutionResult || resolutionResult.resolved.length === 0) {
      setError('Cannot create playlist: no tracks have been resolved.');
      return;
    }

    setCreating(true);
    setError(null);

    try {
      const result = await api.createPlaylist(profile, resolutionResult.resolved);
      onPlaylistCreated(result);
    } catch (err) {
      setError(err.message || 'Failed to create Spotify playlist.');
    } finally {
      setCreating(false);
    }
  };

  const resolvedTracks = resolutionResult?.resolved || [];
  const unresolvedTracks = resolutionResult?.unresolved || [];
  const isCreated = !!playlistResult;

  return (
    <div className="spotify-playlist-container">
      {/* Workflow Summary Header */}
      <div className="spotify-summary-box">
        <div className="spotify-summary-item">
          <span className="summary-label">Target Mood</span>
          <span className="summary-value">
            {profile.core_emotion} → {profile.branch} → {profile.specific_emotion}
          </span>
        </div>
        <div className="spotify-summary-item">
          <span className="summary-label">Validated Candidates</span>
          <span className="summary-value highlight">
            {parsedSongs.length} Songs
          </span>
        </div>
      </div>

      {/* Track Resolution Phase */}
      {!resolutionResult && !isCreated && (
        <div className="resolution-prompt-action" style={{ marginTop: '1.25rem' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Search Spotify's catalog to match song titles and artists to authoritative Spotify track URIs.
          </p>
          <button
            id="resolve-tracks-btn"
            className="btn btn-primary"
            disabled={resolving}
            onClick={handleResolve}
          >
            {resolving ? 'Searching Spotify Catalog...' : 'Resolve Tracks on Spotify'}
          </button>
        </div>
      )}

      {/* Resolution Results Display */}
      {resolutionResult && !isCreated && (
        <div className="resolution-results-card" style={{ marginTop: '1.25rem' }}>
          <div className="resolution-stats-bar">
            <span className="status-pill status-online">
              <span className="status-dot"></span>
              {resolvedTracks.length} / {parsedSongs.length} Tracks Resolved
            </span>

            {unresolvedTracks.length > 0 && (
              <span className="status-pill status-offline">
                <span className="status-dot"></span>
                {unresolvedTracks.length} Unresolved
              </span>
            )}
          </div>

          {/* Unresolved tracks callout */}
          {unresolvedTracks.length > 0 && (
            <div className="unresolved-callout">
              <div className="unresolved-header">
                <strong>Unresolved Songs (Not found on Spotify):</strong>
              </div>
              <ul className="unresolved-list">
                {unresolvedTracks.map((u, i) => (
                  <li key={i} className="unresolved-item">
                    <span className="unresolved-name">
                      {u.title} — {u.artist}
                    </span>
                    {u.reason && <span className="unresolved-reason">({u.reason})</span>}
                  </li>
                ))}
              </ul>
              <p className="unresolved-note">
                The playlist will be created using the {resolvedTracks.length} successfully resolved tracks.
              </p>
            </div>
          )}

          {/* Playlist Creation Trigger */}
          <div className="playlist-creation-actions" style={{ marginTop: '1.25rem' }}>
            {resolvedTracks.length > 0 ? (
              <button
                id="create-playlist-btn"
                className="btn btn-primary btn-large"
                disabled={creating}
                onClick={handleCreatePlaylist}
              >
                {creating
                  ? 'Creating Spotify Playlist...'
                  : `Create Playlist with ${resolvedTracks.length} Tracks`}
              </button>
            ) : (
              <div className="error-banner">
                Zero tracks could be resolved on Spotify. Please verify your song titles and artists in Step 4.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Playlist Created Success Screen */}
      {isCreated && (
        <div className="playlist-success-card" id="playlist-success-result">
          <div className="success-icon-badge">✓</div>
          <h3 className="success-title">Spotify Playlist Created!</h3>
          <p className="success-name">{playlistResult.playlist_name}</p>

          <div className="success-meta">
            <span className="meta-pill">
              🎵 {playlistResult.tracks_added} tracks added
            </span>
            <span className="meta-pill">
              ID: <code>{playlistResult.playlist_id}</code>
            </span>
          </div>

          {playlistResult.playlist_url && (
            <div className="success-action" style={{ marginTop: '1.5rem' }}>
              <a
                id="open-spotify-btn"
                href={playlistResult.playlist_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary btn-large"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
                </svg>
                Open in Spotify
              </a>
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="error-banner" style={{ marginTop: '1.25rem' }}>
          <strong>Spotify Error:</strong> {error}
        </div>
      )}
    </div>
  );
}

export default SpotifyPlaylist;
