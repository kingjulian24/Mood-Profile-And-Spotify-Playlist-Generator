import React, { useState, useEffect } from 'react';
import { api } from './api/client';

export function App() {
  const [backendStatus, setBackendStatus] = useState({
    connected: false,
    loading: true,
    data: null,
    error: null,
  });

  const [config, setConfig] = useState(null);
  const [taxonomy, setTaxonomy] = useState(null);

  useEffect(() => {
    async function checkBackendConnection() {
      try {
        const [health, cfg, tax] = await Promise.all([
          api.getHealth(),
          api.getConfig(),
          api.getTaxonomy(),
        ]);
        setBackendStatus({
          connected: true,
          loading: false,
          data: health,
          error: null,
        });
        setConfig(cfg);
        setTaxonomy(tax);
      } catch (err) {
        setBackendStatus({
          connected: false,
          loading: false,
          data: null,
          error: err.message,
        });
      }
    }

    checkBackendConnection();
  }, []);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-badge">
          <span>Context System Design v0.1</span>
        </div>
        <h1 className="header-title">Mood-Based Spotify Playlist Generator</h1>
        <p className="header-subtitle">
          Transform your current emotional state into a curated Spotify playlist.
        </p>

        {/* Backend Connection Status */}
        <div style={{ marginTop: '1rem' }}>
          {backendStatus.loading ? (
            <span className="status-pill status-online">Checking Python backend...</span>
          ) : backendStatus.connected ? (
            <span className="status-pill status-online">
              <span className="status-dot"></span>
              Backend API Connected (v{backendStatus.data?.version})
            </span>
          ) : (
            <span className="status-pill status-offline">
              <span className="status-dot"></span>
              Backend Disconnected: Start server with <code>python3 main.py --serve</code>
            </span>
          )}
        </div>
      </header>

      {/* Progressive Workflow Shell */}
      <main>
        {/* Step 1: Your Mood */}
        <section className="card" id="step-mood">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 1</span>
              <h2 className="card-title">Your Mood</h2>
            </div>
            {taxonomy && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {taxonomy.core_emotions?.length} Core Emotions Available
              </span>
            )}
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Select your core emotion, branch, specific emotion, and emotional intensity.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.75rem', opacity: 0.85 }}>
            <div className="form-group">
              <label className="form-label">Core Emotion</label>
              <select className="form-select" disabled>
                <option>Joy (Select in Task 013)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Branch</label>
              <select className="form-select" disabled>
                <option>Excited</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Specific Emotion</label>
              <select className="form-select" disabled>
                <option>Energetic</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Intensity (1–10)</label>
              <select className="form-select" disabled>
                <option>8 — Positive / Stable</option>
              </select>
            </div>
          </div>
        </section>

        {/* Step 2: Mood Profile */}
        <section className="card" id="step-profile">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 2</span>
              <h2 className="card-title">Mood Profile</h2>
            </div>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            The structured emotional context modeling representing your selections.
          </p>
        </section>

        {/* Step 3: Recommendation Prompt */}
        <section className="card" id="step-prompt">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 3</span>
              <h2 className="card-title">Recommendation Prompt</h2>
            </div>
            {config && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {config.song_count} songs ({config.output_format.toUpperCase()})
              </span>
            )}
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Copyable prompt requesting machine-readable song recommendations from an external chatbot.
          </p>
        </section>

        {/* Step 4: Song Recommendations */}
        <section className="card" id="step-import">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 4</span>
              <h2 className="card-title">Song Recommendations</h2>
            </div>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Paste the chatbot's machine-readable response to validate and prepare for Spotify resolution.
          </p>
        </section>

        {/* Step 5: Spotify Resolution & Playlist */}
        <section className="card" id="step-spotify">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 5</span>
              <h2 className="card-title">Spotify Playlist</h2>
            </div>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Deterministic track resolution and Spotify playlist creation.
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        Mood-Based Spotify Playlist Generator • GUI Architecture v0.1 • Python Backend & React Frontend
      </footer>
    </div>
  );
}

export default App;
