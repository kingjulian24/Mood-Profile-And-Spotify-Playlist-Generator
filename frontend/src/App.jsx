import React, { useState, useEffect } from 'react';
import { api } from './api/client';
import { MoodSelection } from './components/MoodSelection';
import { MoodProfileView } from './components/MoodProfileView';
import { PromptView } from './components/PromptView';
import { SongImport } from './components/SongImport';
import { SpotifyPlaylist } from './components/SpotifyPlaylist';

export function App() {
  const [backendStatus, setBackendStatus] = useState({
    connected: false,
    loading: true,
    data: null,
    error: null,
  });

  const [spotifyStatus, setSpotifyStatus] = useState({
    authenticated: false,
    loading: true,
    user: null,
  });

  const [config, setConfig] = useState(null);
  const [taxonomy, setTaxonomy] = useState(null);

  // Mood Selection States
  const [selectedCore, setSelectedCore] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [selectedSpecific, setSelectedSpecific] = useState('');
  const [intensity, setIntensity] = useState(7);

  // Generated Profile State
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [profileError, setProfileError] = useState(null);

  // Generated Prompt State
  const [promptData, setPromptData] = useState(null);
  const [loadingPrompt, setLoadingPrompt] = useState(false);
  const [promptError, setPromptError] = useState(null);

  // Imported Songs State
  const [parsedSongs, setParsedSongs] = useState(null);

  // Spotify Resolution & Playlist States
  const [resolutionResult, setResolutionResult] = useState(null);
  const [playlistResult, setPlaylistResult] = useState(null);

  useEffect(() => {
    async function initApp() {
      try {
        const [health, cfg, tax, spot] = await Promise.all([
          api.getHealth(),
          api.getConfig(),
          api.getTaxonomy(),
          api.getSpotifyStatus().catch(() => ({ authenticated: false, user: null })),
        ]);
        setBackendStatus({
          connected: true,
          loading: false,
          data: health,
          error: null,
        });
        setConfig(cfg);
        setTaxonomy(tax);
        setSpotifyStatus({
          authenticated: spot.authenticated,
          loading: false,
          user: spot.user,
        });
      } catch (err) {
        setBackendStatus({
          connected: false,
          loading: false,
          data: null,
          error: err.message,
        });
        setSpotifyStatus({
          authenticated: false,
          loading: false,
          user: null,
        });
      }
    }

    initApp();
  }, []);

  const refreshSpotifyStatus = async () => {
    try {
      const spot = await api.getSpotifyStatus();
      setSpotifyStatus({
        authenticated: spot.authenticated,
        loading: false,
        user: spot.user || (spot.display_name ? { id: spot.user_id, display_name: spot.display_name } : null),
      });
      return spot.authenticated;
    } catch {
      setSpotifyStatus({
        authenticated: false,
        loading: false,
        user: null,
      });
      return false;
    }
  };

  const handleConnectSpotify = async () => {
    try {
      const { auth_url } = await api.startSpotifyAuth();
      const authWindow = window.open(auth_url, 'SpotifyOAuth', 'width=600,height=750,menubar=no,toolbar=no');

      // Poll Spotify status until connected or window closed
      const interval = setInterval(async () => {
        const isAuth = await refreshSpotifyStatus();
        if (isAuth || (authWindow && authWindow.closed)) {
          clearInterval(interval);
        }
      }, 1500);
    } catch (err) {
      alert(err.message || 'Failed to start Spotify authentication.');
    }
  };

  const handleDisconnectSpotify = async () => {
    try {
      await api.disconnectSpotify();
      await refreshSpotifyStatus();
      setResolutionResult(null);
      setPlaylistResult(null);
    } catch (err) {
      alert(err.message || 'Failed to disconnect Spotify.');
    }
  };

  // Invalidation handlers for progressive selection
  const resetDownstream = () => {
    setProfile(null);
    setProfileError(null);
    setPromptData(null);
    setPromptError(null);
    setParsedSongs(null);
    setResolutionResult(null);
    setPlaylistResult(null);
  };

  const handleSelectCore = (coreName) => {
    setSelectedCore(coreName);
    setSelectedBranch('');
    setSelectedSpecific('');
    resetDownstream();
  };

  const handleSelectBranch = (branchName) => {
    setSelectedBranch(branchName);
    setSelectedSpecific('');
    resetDownstream();
  };

  const handleSelectSpecific = (specificName) => {
    setSelectedSpecific(specificName);
    resetDownstream();
  };

  const handleSelectIntensity = (intensityVal) => {
    setIntensity(intensityVal);
    resetDownstream();
  };

  const handleStartOver = () => {
    setSelectedCore('');
    setSelectedBranch('');
    setSelectedSpecific('');
    setIntensity(7);
    resetDownstream();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const fetchPrompt = async (targetProfile) => {
    setLoadingPrompt(true);
    setPromptError(null);
    try {
      const pData = await api.generatePrompt({ profile: targetProfile });
      setPromptData(pData);
    } catch (err) {
      setPromptError(err.message || 'Failed to generate recommendation prompt from backend.');
    } finally {
      setLoadingPrompt(false);
    }
  };

  const handleGenerateProfile = async () => {
    if (!selectedCore || !selectedBranch || !selectedSpecific || !intensity) return;

    setLoadingProfile(true);
    setProfileError(null);
    setPromptData(null);
    setParsedSongs(null);
    setResolutionResult(null);
    setPlaylistResult(null);

    try {
      const generatedProfile = await api.generateProfile({
        core_emotion: selectedCore,
        branch: selectedBranch,
        specific_emotion: selectedSpecific,
        intensity: intensity,
      });
      setProfile(generatedProfile);
      // Immediately request prompt generation from backend
      await fetchPrompt(generatedProfile);
    } catch (err) {
      setProfileError(err.message || 'Failed to generate mood profile.');
    } finally {
      setLoadingProfile(false);
    }
  };

  // Determine current active step index (1-based)
  const currentStep = playlistResult ? 5 : parsedSongs ? 5 : promptData ? 4 : profile ? 3 : selectedCore && selectedBranch && selectedSpecific ? 2 : 1;

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

        {/* System & Authentication Status Indicators */}
        <div className="header-status-row">
          {backendStatus.loading ? (
            <span className="status-pill status-online">Checking Python backend...</span>
          ) : backendStatus.connected ? (
            <span className="status-pill status-online" title="Python REST API Server running">
              <span className="status-dot"></span>
              Backend API (v{backendStatus.data?.version})
            </span>
          ) : (
            <span className="status-pill status-offline">
              <span className="status-dot"></span>
              Backend Disconnected: <code>python3 main.py --serve</code>
            </span>
          )}

          {!spotifyStatus.loading && (
            spotifyStatus.authenticated ? (
              <div className="header-auth-group">
                <span className="status-pill status-spotify-connected" title={`Logged in as ${spotifyStatus.user?.display_name || spotifyStatus.user?.id}`}>
                  <span className="status-dot" style={{ background: '#1db954' }}></span>
                  Spotify: {spotifyStatus.user?.display_name || 'Connected'}
                  {spotifyStatus.user?.id && <span style={{ opacity: 0.7, marginLeft: '4px' }}>({spotifyStatus.user.id})</span>}
                </span>
                <button
                  id="disconnect-spotify-btn"
                  className="btn btn-tiny btn-secondary"
                  onClick={handleDisconnectSpotify}
                  title="Disconnect Spotify account"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <div className="header-auth-group">
                <span className="status-pill status-spotify-disconnected" title="Connect your Spotify account">
                  <span className="status-dot" style={{ background: '#f59e0b' }}></span>
                  Spotify: Not Connected
                </span>
                <button
                  id="connect-spotify-btn"
                  className="btn btn-tiny btn-spotify"
                  onClick={handleConnectSpotify}
                >
                  Connect Spotify
                </button>
              </div>
            )
          )}
        </div>

        {/* Workflow Progress Stepper */}
        <nav className="workflow-stepper" aria-label="Workflow Steps">
          {[
            { num: 1, label: 'Mood' },
            { num: 2, label: 'Profile' },
            { num: 3, label: 'Prompt' },
            { num: 4, label: 'Songs' },
            { num: 5, label: 'Playlist' },
          ].map((s) => {
            const isCompleted = s.num < currentStep || (s.num === 5 && playlistResult);
            const isCurrent = s.num === currentStep && !playlistResult;
            return (
              <div
                key={s.num}
                className={`stepper-item ${isCompleted ? 'completed' : ''} ${isCurrent ? 'current' : ''}`}
              >
                <div className="stepper-circle">
                  {isCompleted ? '✓' : s.num}
                </div>
                <span className="stepper-label">{s.label}</span>
              </div>
            );
          })}
        </nav>
      </header>

      {/* Progressive Workflow Cards */}
      <main>
        {/* Step 1: Your Mood */}
        <section className={`card ${currentStep === 1 ? 'card-active' : ''}`} id="step-mood">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 1</span>
              <h2 className="card-title">Your Mood</h2>
            </div>
            {profile ? (
              <span className="status-pill status-online">✓ Completed</span>
            ) : (
              taxonomy && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {taxonomy.core_emotions?.length} Core Emotions Available
                </span>
              )
            )}
          </div>

          <MoodSelection
            taxonomy={taxonomy}
            selectedCore={selectedCore}
            onSelectCore={handleSelectCore}
            selectedBranch={selectedBranch}
            onSelectBranch={handleSelectBranch}
            selectedSpecific={selectedSpecific}
            onSelectSpecific={handleSelectSpecific}
            intensity={intensity}
            onSelectIntensity={handleSelectIntensity}
            onGenerateProfile={handleGenerateProfile}
            loading={loadingProfile}
          />

          {profileError && (
            <div className="error-banner" style={{ marginTop: '1rem' }}>
              {profileError}
            </div>
          )}
        </section>

        {/* Step 2: Mood Profile */}
        <section className={`card ${!profile ? 'card-dimmed' : ''}`} id="step-profile">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 2</span>
              <h2 className="card-title">Mood Profile</h2>
            </div>
            {profile ? (
              <span className="status-pill status-online">
                <span className="status-dot"></span>
                Active Profile
              </span>
            ) : (
              <span className="status-pill status-dimmed">Waiting for Step 1</span>
            )}
          </div>

          <MoodProfileView profile={profile} />
        </section>

        {/* Step 3: Recommendation Prompt */}
        <section className={`card ${!promptData ? 'card-dimmed' : ''}`} id="step-prompt">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 3</span>
              <h2 className="card-title">Recommendation Prompt</h2>
            </div>
            {promptData ? (
              <span className="status-pill status-online">
                <span className="status-dot"></span>
                Prompt Ready
              </span>
            ) : config ? (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                {config.song_count} songs ({config.output_format?.toUpperCase()})
              </span>
            ) : (
              <span className="status-pill status-dimmed">Waiting for Step 2</span>
            )}
          </div>

          <PromptView
            promptData={promptData}
            loading={loadingPrompt}
            error={promptError}
            onRetry={() => profile && fetchPrompt(profile)}
            config={config}
          />
        </section>

        {/* Step 4: Song Recommendations */}
        <section className={`card ${!promptData ? 'card-dimmed' : ''}`} id="step-import">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 4</span>
              <h2 className="card-title">Song Recommendations</h2>
            </div>
            {parsedSongs ? (
              <span className="status-pill status-online">
                <span className="status-dot"></span>
                {parsedSongs.length} Songs Validated
              </span>
            ) : (
              <span className="status-pill status-dimmed">
                {promptData ? 'Paste Chatbot Output' : 'Waiting for Step 3'}
              </span>
            )}
          </div>

          <SongImport
            config={config}
            promptData={promptData}
            parsedSongs={parsedSongs}
            onSongsParsed={(songs) => {
              setParsedSongs(songs);
              setResolutionResult(null);
              setPlaylistResult(null);
            }}
            onClearSongs={() => {
              setParsedSongs(null);
              setResolutionResult(null);
              setPlaylistResult(null);
            }}
            disabled={!promptData}
          />
        </section>

        {/* Step 5: Spotify Resolution & Playlist */}
        <section className={`card ${!parsedSongs ? 'card-dimmed' : ''}`} id="step-spotify">
          <div className="card-header">
            <div>
              <span className="card-step-badge">Step 5</span>
              <h2 className="card-title">Spotify Playlist</h2>
            </div>
            {playlistResult ? (
              <span className="status-pill status-online">
                <span className="status-dot"></span>
                Playlist Created
              </span>
            ) : (
              <span className="status-pill status-dimmed">
                {parsedSongs ? 'Ready to Resolve' : 'Waiting for Step 4'}
              </span>
            )}
          </div>

          <SpotifyPlaylist
            profile={profile}
            parsedSongs={parsedSongs}
            resolutionResult={resolutionResult}
            onResolutionDone={(res) => setResolutionResult(res)}
            playlistResult={playlistResult}
            onPlaylistCreated={(res) => setPlaylistResult(res)}
            spotifyStatus={spotifyStatus}
            onConnectSpotify={handleConnectSpotify}
            disabled={!parsedSongs || parsedSongs.length === 0}
          />
        </section>

        {/* Start Over Action Button */}
        {(profile || parsedSongs || playlistResult) && (
          <div style={{ textAlign: 'center', margin: '2rem 0 1rem' }}>
            <button
              id="start-over-btn"
              className="btn btn-secondary"
              onClick={handleStartOver}
            >
              Start New Playlist Session
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        Mood-Based Spotify Playlist Generator • Context System Design v0.1 • Python Backend & React Frontend
      </footer>
    </div>
  );
}

export default App;
