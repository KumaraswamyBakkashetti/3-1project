import React, { useState } from 'react';

function CopyButton({ textToCopy = '', label = 'Copy', size = 12, className = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e) => {
    e && e.stopPropagation && e.stopPropagation();
    try {
      if (textToCopy === undefined || textToCopy === null) return;
      await navigator.clipboard.writeText(String(textToCopy));
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch (err) {
      try {
        const ta = document.createElement('textarea');
        ta.value = String(textToCopy);
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        setCopied(true);
        setTimeout(() => setCopied(false), 1400);
      } catch (e) {
        console.error('Copy failed', e);
      }
    }
  };

  const baseStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 6,
    padding: '0 6px',
    height: 22,
    fontSize: size,
    borderRadius: 4,
    border: 'none',
    background: 'transparent',
    color: 'inherit',
    cursor: 'pointer'
  };

  const copiedStyle = {
    color: '#10b981'
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={`copy-button ${className}`}
      title={copied ? 'Copied!' : label}
      style={{ ...baseStyle, ...(copied ? copiedStyle : {}) }}
    >
      {/* Copy icon (outline) */}
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M16 21H8a2 2 0 0 1-2-2V7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        <rect x="8" y="3" width="13" height="13" rx="2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      <span style={{ lineHeight: 1 }}>{copied ? 'Copied' : label}</span>
    </button>
  );
}

export default CopyButton;
