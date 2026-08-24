/**
 * Client interface for communicating with the Python backend API.
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `HTTP error ${response.status}`);
    }

    return data;
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'} ${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // System & Config
  getHealth: () => request('/health'),
  getConfig: () => request('/config'),
  getTaxonomy: () => request('/taxonomy'),

  // Profile & Prompt Generation
  generateProfile: (params) =>
    request('/profile', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  generatePrompt: (params) =>
    request('/prompt', {
      method: 'POST',
      body: JSON.stringify(params),
    }),

  // Song Recommendations & Validation
  parseSongs: (rawText, formatHint) =>
    request('/songs/parse', {
      method: 'POST',
      body: JSON.stringify({ raw_text: rawText, format_hint: formatHint }),
    }),

  // Spotify Operations
  getSpotifyStatus: () => request('/spotify/status'),
  startSpotifyAuth: () => request('/spotify/auth/start'),
  disconnectSpotify: () =>
    request('/spotify/auth/disconnect', {
      method: 'POST',
    }),

  resolveTracks: (songs) =>
    request('/spotify/resolve', {
      method: 'POST',
      body: JSON.stringify({ songs }),
    }),

  createPlaylist: (profile, tracks) =>
    request('/spotify/playlist', {
      method: 'POST',
      body: JSON.stringify({ profile, tracks }),
    }),
};
