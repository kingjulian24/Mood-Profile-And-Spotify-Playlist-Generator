import React, { useState } from 'react';
import { api } from '../api/client';

export function SongImport({ config, promptData, parsedSongs, onSongsParsed, onClearSongs, disabled }) {
  const [rawText, setRawText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const expectedFormat = (promptData?.output_format || config?.output_format || 'json').toUpperCase();

  const handleParse = async () => {
    if (!rawText.trim()) {
      setError('Please paste the chatbot response before parsing.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.parseSongs(rawText.trim(), promptData?.output_format || config?.output_format);
      if (response.valid && response.songs && response.songs.length > 0) {
        onSongsParsed(response.songs);
      } else {
        setError(response.error || 'Failed to parse songs from the response.');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while communicating with the backend parser.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setRawText('');
    setError(null);
    onClearSongs();
  };

  if (disabled) {
    return (
      <div className="empty-import-state">
        <p>Complete Steps 1–3 to generate your prompt before importing chatbot recommendations.</p>
      </div>
    );
  }

  return (
    <div className="song-import-container">
      {/* Subheader & Format Badge */}
      <div className="import-meta-header">
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: 0 }}>
          Paste the structured song recommendations returned by your chatbot.
        </p>
        <span className="import-format-badge">
          Expected Format: <strong>{expectedFormat}</strong>
        </span>
      </div>

      {/* Input Text Area */}
      <div className="form-group" style={{ marginTop: '1rem', marginBottom: '1rem' }}>
        <textarea
          id="chatbot-response-input"
          className="form-textarea import-textarea"
          rows={7}
          placeholder={`Paste ${expectedFormat} response here...\n\nExample:\n{\n  "songs": [\n    {\n      "title": "September",\n      "artist": "Earth, Wind & Fire"\n    }\n  ]\n}`}
          value={rawText}
          onChange={(e) => {
            setRawText(e.target.value);
            if (error) setError(null);
          }}
        />
      </div>

      {/* Action Buttons */}
      <div className="import-actions">
        <button
          id="parse-songs-btn"
          className="btn btn-primary"
          disabled={!rawText.trim() || loading}
          onClick={handleParse}
        >
          {loading ? 'Validating & Parsing...' : 'Parse Songs'}
        </button>

        {rawText && (
          <button
            id="clear-songs-btn"
            className="btn btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear Input
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-banner" style={{ marginTop: '1.25rem' }}>
          <strong>Import Error:</strong> {error}
        </div>
      )}

      {/* Parsed Songs Table / List */}
      {parsedSongs && parsedSongs.length > 0 && (
        <div className="parsed-songs-section">
          <div className="parsed-songs-header">
            <div className="parsed-count-badge">
              <span className="status-dot" style={{ background: '#4ade80' }}></span>
              <span>✓ {parsedSongs.length} Songs Successfully Validated</span>
            </div>
          </div>

          <div className="table-responsive">
            <table className="songs-table">
              <thead>
                <tr>
                  <th style={{ width: '48px' }}>#</th>
                  <th>Title</th>
                  <th>Artist</th>
                </tr>
              </thead>
              <tbody>
                {parsedSongs.map((song, idx) => (
                  <tr key={`${idx}-${song.title}`}>
                    <td className="song-index-cell">{idx + 1}</td>
                    <td className="song-title-cell">{song.title}</td>
                    <td className="song-artist-cell">{song.artist}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default SongImport;
