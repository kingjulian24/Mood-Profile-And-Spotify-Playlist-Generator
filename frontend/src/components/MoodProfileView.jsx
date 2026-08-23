import React from 'react';

export function MoodProfileView({ profile }) {
  if (!profile) {
    return (
      <div className="empty-profile-state">
        <p>Complete your mood selection above and click <strong>Generate Profile</strong> to view your structured emotional context.</p>
      </div>
    );
  }

  return (
    <div className="mood-profile-display">
      <div className="profile-hierarchy">
        <span className="hierarchy-crumb">{profile.core_emotion}</span>
        <span className="hierarchy-separator">→</span>
        <span className="hierarchy-crumb">{profile.branch}</span>
        <span className="hierarchy-separator">→</span>
        <span className="hierarchy-crumb active">{profile.specific_emotion}</span>
      </div>

      <div className="profile-grid">
        <div className="profile-item">
          <span className="profile-item-label">Intensity</span>
          <span className="profile-item-value highlight">{profile.intensity} / 10</span>
          {profile.intensity_label && (
            <span className="profile-item-sub">{profile.intensity_label}</span>
          )}
        </div>

        <div className="profile-item">
          <span className="profile-item-label">Core Emotion</span>
          <span className="profile-item-value">{profile.core_emotion}</span>
        </div>

        <div className="profile-item">
          <span className="profile-item-label">Branch</span>
          <span className="profile-item-value">{profile.branch}</span>
        </div>

        <div className="profile-item">
          <span className="profile-item-label">Specific Emotion</span>
          <span className="profile-item-value">{profile.specific_emotion}</span>
        </div>
      </div>

      <div className="mood-code-box">
        <span className="mood-code-label">Canonical Mood Code:</span>
        <code className="mood-code-badge">{profile.code}</code>
      </div>
    </div>
  );
}

export default MoodProfileView;
