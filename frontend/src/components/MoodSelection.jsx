import React from 'react';

export function MoodSelection({
  taxonomy,
  selectedCore,
  onSelectCore,
  selectedBranch,
  onSelectBranch,
  selectedSpecific,
  onSelectSpecific,
  intensity,
  onSelectIntensity,
  onGenerateProfile,
  loading,
}) {
  if (!taxonomy || !taxonomy.core_emotions) {
    return <div className="loading-text">Loading mood taxonomy...</div>;
  }

  // Find active core object and its branches
  const activeCoreObj = taxonomy.core_emotions.find((c) => c.name === selectedCore);
  const availableBranches = activeCoreObj ? activeCoreObj.branches || [] : [];

  // Find active branch object and its specific emotions
  const activeBranchObj = availableBranches.find((b) => b.name === selectedBranch);
  const availableSpecifics = activeBranchObj ? activeBranchObj.specific_emotions || [] : [];

  // Find intensity bracket info
  const intensityLevel = taxonomy.intensity_levels?.find(
    (lvl) => intensity >= lvl.min && intensity <= lvl.max
  );

  const isComplete = selectedCore && selectedBranch && selectedSpecific && intensity;

  return (
    <div className="mood-selection-container">
      {/* 1. Core Emotion */}
      <div className="form-group">
        <label className="form-label" htmlFor="core-emotion-select">
          1. Core Emotion
        </label>
        <select
          id="core-emotion-select"
          className="form-select"
          value={selectedCore || ''}
          onChange={(e) => onSelectCore(e.target.value || null)}
        >
          <option value="">-- Choose a core emotion --</option>
          {taxonomy.core_emotions.map((core) => (
            <option key={core.name} value={core.name}>
              [{core.code_letter}] {core.name} — {core.description}
            </option>
          ))}
        </select>
      </div>

      {/* 2. Branch */}
      <div className="form-group">
        <label className="form-label" htmlFor="branch-select">
          2. Branch
        </label>
        <select
          id="branch-select"
          className="form-select"
          value={selectedBranch || ''}
          disabled={!selectedCore}
          onChange={(e) => onSelectBranch(e.target.value || null)}
        >
          <option value="">
            {selectedCore ? '-- Choose a branch --' : '-- Select a core emotion first --'}
          </option>
          {availableBranches.map((b) => (
            <option key={b.name} value={b.name}>
              {b.name} — {b.description}
            </option>
          ))}
        </select>
      </div>

      {/* 3. Specific Emotion */}
      <div className="form-group">
        <label className="form-label" htmlFor="specific-emotion-select">
          3. Specific Emotion
        </label>
        <select
          id="specific-emotion-select"
          className="form-select"
          value={selectedSpecific || ''}
          disabled={!selectedBranch}
          onChange={(e) => onSelectSpecific(e.target.value || null)}
        >
          <option value="">
            {selectedBranch ? '-- Choose a specific emotion --' : '-- Select a branch first --'}
          </option>
          {availableSpecifics.map((spec) => (
            <option key={spec} value={spec}>
              {spec}
            </option>
          ))}
        </select>
      </div>

      {/* 4. Emotional Intensity */}
      <div className="form-group">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label className="form-label" htmlFor="intensity-input" style={{ margin: 0 }}>
            4. Emotional Intensity: <strong style={{ color: 'var(--accent-spotify-hover)' }}>{intensity} / 10</strong>
          </label>
          {intensityLevel && (
            <span className="intensity-label-badge">
              {intensityLevel.label}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <input
            id="intensity-input"
            type="range"
            min={taxonomy.intensity_min || 1}
            max={taxonomy.intensity_max || 10}
            value={intensity}
            className="form-range"
            onChange={(e) => onSelectIntensity(parseInt(e.target.value, 10))}
          />
        </div>
        {intensityLevel && (
          <p className="intensity-desc-text">
            {intensityLevel.description}
          </p>
        )}
      </div>

      {/* Action Button */}
      <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
        <button
          id="generate-profile-btn"
          className="btn btn-primary"
          disabled={!isComplete || loading}
          onClick={onGenerateProfile}
        >
          {loading ? 'Generating Profile...' : 'Generate Profile'}
        </button>
      </div>
    </div>
  );
}

export default MoodSelection;
