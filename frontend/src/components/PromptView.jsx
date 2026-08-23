import React, { useState } from 'react';

export function PromptView({ promptData, loading, error, onRetry, config }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!promptData?.prompt) return;
    try {
      await navigator.clipboard.writeText(promptData.prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch (err) {
      console.error('Failed to copy prompt to clipboard:', err);
    }
  };

  if (loading) {
    return (
      <div className="empty-prompt-state">
        <p>Generating recommendation prompt from your mood profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-banner">
        <p>{error}</p>
        {onRetry && (
          <button
            className="btn btn-secondary"
            style={{ marginTop: '0.75rem', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
            onClick={onRetry}
          >
            Retry Generation
          </button>
        )}
      </div>
    );
  }

  if (!promptData || !promptData.prompt) {
    return (
      <div className="empty-prompt-state">
        <p>
          Generate your Mood Profile in Step 1 to assemble your machine-readable recommendation prompt.
        </p>
      </div>
    );
  }

  return (
    <div className="prompt-display-container">
      <div className="prompt-meta-header">
        <div className="prompt-meta-info">
          <span className="prompt-format-tag">
            Format: {promptData.output_format?.toUpperCase() || config?.output_format?.toUpperCase()}
          </span>
          <span className="prompt-count-tag">
            {promptData.song_count || config?.song_count} Recommendations Requested
          </span>
        </div>
        <button
          id="copy-prompt-btn"
          className={`btn ${copied ? 'btn-copied' : 'btn-primary'}`}
          onClick={handleCopy}
          aria-label="Copy recommendation prompt to clipboard"
        >
          {copied ? (
            <>
              <span>✓</span> Copied to Clipboard!
            </>
          ) : (
            <>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              Copy Prompt
            </>
          )}
        </button>
      </div>

      <div className="prompt-textbox-wrapper">
        <pre className="prompt-code-block">{promptData.prompt}</pre>
      </div>

      <div className="prompt-instructions">
        <p>
          💡 <strong>Next Step:</strong> Paste the copied prompt into an external chatbot (ChatGPT, Claude, Gemini, etc.). Then copy the chatbot's response to import below in <strong>Step 4</strong>.
        </p>
      </div>
    </div>
  );
}

export default PromptView;
