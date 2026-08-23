#!/usr/bin/env bash
# ==============================================================================
# Spotify API Environment Variables Template
#
# Instructions:
# 1. Copy this file to `set-spotify-env.sh`:
#    cp set-spotify-env.example.sh set-spotify-env.sh
# 2. Fill in your Spotify Developer Client ID and Client Secret below.
# 3. Source the script into your current shell:
#    source ./set-spotify-env.sh
#
# Note: `set-spotify-env.sh` is ignored by Git to protect your credentials.
# ==============================================================================

export SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"
export SPOTIFY_REDIRECT_URI="http://127.0.0.1:8888/callback"
