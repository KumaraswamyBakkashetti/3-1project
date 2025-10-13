import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRun } from '../api';
import './AdminPromptDetail.css';

function AdminPromptDetail() {
  const { userId, promptId } = useParams();
  const navigate = useNavigate();
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    loadPromptDetail();
  }, [promptId]);

  const loadPromptDetail = async () => {
    try {
      setLoading(true);
      const data = await getRun(promptId);
      setRun(data);
    } catch (error) {
      console.error('Failed to load prompt details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadJSON = () => {
    if (!run) return;
    
    setDownloading(true);
    const dataStr = JSON.stringify(run, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `prompt_${promptId}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    setDownloading(false);
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#10b981';
    if (score >= 0.6) return '#3b82f6';
    if (score >= 0.4) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <div className="admin-prompt-detail">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading prompt details...</p>
        </div>
      </div>
    );
  }

  if (!run) {
    return (
      <div className="admin-prompt-detail">
        <div className="empty-state">
          <div className="empty-icon">❌</div>
          <p>Prompt not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-prompt-detail">
      {/* Header */}
      <div className="detail-header">
        <button 
          className="back-button" 
          onClick={() => navigate(`/admin/user/${userId}`)}
        >
          ← Back to {run.username}'s Prompts
        </button>
        <button 
          className="download-json-btn"
          onClick={handleDownloadJSON}
          disabled={downloading}
        >
          {downloading ? '⏳ Downloading...' : '📥 Download JSON'}
        </button>
      </div>

      {/* Prompt Overview */}
      <div className="prompt-overview">
        <div className="overview-header">
          <h1>🔍 Prompt Details</h1>
          <span className="prompt-id">ID: {run._id}</span>
        </div>
        
        <div className="overview-meta">
          <div className="meta-item">
            <span className="meta-label">👤 User:</span>
            <span className="meta-value">{run.username}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">📅 Date:</span>
            <span className="meta-value">{new Date(run.created_at).toLocaleString()}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">🆔 Run ID:</span>
            <span className="meta-value">{run._id}</span>
          </div>
        </div>
      </div>

      {/* Prompt Text */}
      <div className="section-card">
        <h2>📝 Prompt Text</h2>
        <div className="prompt-text-display">
          {run.task}
        </div>
      </div>

      {/* Code Comparison */}
      <div className="code-comparison">
        <div className="code-panel">
          <div className="code-panel-header">
            <h3>📄 Initial Code</h3>
            <span className="code-status">First Generation</span>
          </div>
          <pre className="code-block">
            {run.initial_code || run.code || 'No initial code available'}
          </pre>
        </div>

        <div className="code-panel">
          <div className="code-panel-header">
            <h3>✨ Enhanced Code</h3>
            <span className="code-status enhanced">After MAS Enhancement</span>
          </div>
          <pre className="code-block enhanced">
            {run.code || 'No enhanced code available'}
          </pre>
        </div>
      </div>

      {/* MAS Indicators */}
      <div className="section-card">
        <h2>📊 MAS Indicators</h2>
        <div className="indicators-grid">
          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">⭐</span>
              <span className="indicator-label">Personal Score</span>
            </div>
            <div className="indicator-values">
              <div className="value-item">
                <span className="value-label">Initial:</span>
                <span 
                  className="value-number"
                  style={{ color: getScoreColor(run.features?.personal_score || 0) }}
                >
                  {(run.features?.personal_score || 0).toFixed(3)}
                </span>
              </div>
              <div className="value-item">
                <span className="value-label">Final:</span>
                <span 
                  className="value-number"
                  style={{ color: getScoreColor(run.predicted_score || 0) }}
                >
                  {(run.predicted_score || 0).toFixed(3)}
                </span>
              </div>
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">💎</span>
              <span className="indicator-label">Clarity</span>
            </div>
            <div className="indicator-value-single">
              {(run.features?.clarity || 0).toFixed(3)}
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">✅</span>
              <span className="indicator-label">Code Correctness</span>
            </div>
            <div className="indicator-value-single">
              {(run.features?.code_correctness || 0).toFixed(3)}
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">🧩</span>
              <span className="indicator-label">Complexity</span>
            </div>
            <div className="indicator-value-single">
              {(run.features?.complexity || 0).toFixed(3)}
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">🔄</span>
              <span className="indicator-label">Loops</span>
            </div>
            <div className="indicator-value-single">
              {run.features?.loops || 0}
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">⚡</span>
              <span className="indicator-label">Latency</span>
            </div>
            <div className="indicator-value-single">
              {(run.features?.latency || 0).toFixed(2)}s
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">🎯</span>
              <span className="indicator-label">Tokens</span>
            </div>
            <div className="indicator-value-single">
              {run.features?.total_token_usage || 0}
            </div>
          </div>

          <div className="indicator-card">
            <div className="indicator-header">
              <span className="indicator-icon">🤖</span>
              <span className="indicator-label">Agents Used</span>
            </div>
            <div className="indicator-value-single">
              {run.features?.num_nodes || 0}
            </div>
          </div>
        </div>
      </div>

      {/* Per-Agent Breakdown */}
      {run.monitor_data && run.monitor_data.agent_stats && (
        <div className="section-card">
          <h2>👥 Per-Agent Iteration Details</h2>
          <p className="section-description">
            Detailed view of each agent's conversation history, showing initial and final outputs with personal scores
          </p>
          <div className="agents-breakdown">
            {Object.entries(run.monitor_data.agent_stats).map(([agentName, agentData]) => {
              const conversations = agentData.conversations || [];
              const firstConv = conversations[0] || {};
              const lastConv = conversations[conversations.length - 1] || {};
              
              return (
                <div key={agentName} className="agent-card">
                  <div className="agent-header">
                    <span className="agent-icon">
                      {agentName === 'analyzer' ? '🔍' : 
                       agentName === 'coder' ? '💻' : 
                       agentName === 'tester' ? '🧪' : '👁️'}
                    </span>
                    <span className="agent-name">{agentName.charAt(0).toUpperCase() + agentName.slice(1)}</span>
                    <span className="agent-attempts">{conversations.length} iteration{conversations.length > 1 ? 's' : ''}</span>
                  </div>

                  <div className="agent-comparison">
                    {/* Initial Output */}
                    <div className="agent-output-panel">
                      <div className="panel-label">
                        📝 Initial Output
                        {firstConv.personal_score !== undefined && (
                          <span className="score-badge" style={{ backgroundColor: getScoreColor(firstConv.personal_score) + '20', color: getScoreColor(firstConv.personal_score) }}>
                            Score: {firstConv.personal_score.toFixed(3)}
                          </span>
                        )}
                      </div>
                      <pre className="agent-code">
                        {firstConv.output || 'No output available'}
                      </pre>
                      {firstConv.latency !== undefined && (
                        <div className="output-meta">⏱️ {firstConv.latency.toFixed(2)}s</div>
                      )}
                    </div>

                    {conversations.length > 1 && (
                      <>
                        <div className="comparison-arrow">→</div>
                        
                        {/* Final Output */}
                        <div className="agent-output-panel final">
                          <div className="panel-label">
                            ✨ Final Output
                            {lastConv.personal_score !== undefined && (
                              <span className="score-badge" style={{ backgroundColor: getScoreColor(lastConv.personal_score) + '20', color: getScoreColor(lastConv.personal_score) }}>
                                Score: {lastConv.personal_score.toFixed(3)}
                              </span>
                            )}
                          </div>
                          <pre className="agent-code highlighted">
                            {lastConv.output || 'No output available'}
                          </pre>
                          {lastConv.latency !== undefined && (
                            <div className="output-meta">⏱️ {lastConv.latency.toFixed(2)}s</div>
                          )}
                        </div>
                      </>
                    )}
                  </div>

                  {/* Score Progression */}
                  {conversations.length > 1 && firstConv.personal_score !== undefined && lastConv.personal_score !== undefined && (
                    <div className="score-progression">
                      <span className="progression-label">Score Improvement:</span>
                      <span className={`progression-value ${lastConv.personal_score > firstConv.personal_score ? 'positive' : 'neutral'}`}>
                        {firstConv.personal_score.toFixed(3)} → {lastConv.personal_score.toFixed(3)}
                        {lastConv.personal_score > firstConv.personal_score && (
                          <span className="improvement-badge">
                            +{((lastConv.personal_score - firstConv.personal_score) * 100).toFixed(1)}%
                          </span>
                        )}
                      </span>
                    </div>
                  )}

                  {/* All Iterations (if more than 2) */}
                  {conversations.length > 2 && (
                    <details className="all-iterations">
                      <summary>View all {conversations.length} iterations</summary>
                      <div className="iterations-list">
                        {conversations.map((conv, idx) => (
                          <div key={idx} className="iteration-item">
                            <div className="iteration-header">
                              <span className="iteration-number">Iteration {idx + 1}</span>
                              {conv.personal_score !== undefined && (
                                <span className="iteration-score" style={{ color: getScoreColor(conv.personal_score) }}>
                                  Score: {conv.personal_score.toFixed(3)}
                                </span>
                              )}
                            </div>
                            <pre className="iteration-output">{conv.output}</pre>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Collective Score (XGBoost) */}
      <div className="section-card highlight">
        <h2>🎯 Collective Score (XGBoost Prediction)</h2>
        <div className="collective-score-display">
          <div className="score-circle" style={{ borderColor: getScoreColor(run.predicted_score) }}>
            <span className="score-value" style={{ color: getScoreColor(run.predicted_score) }}>
              {(run.predicted_score || 0).toFixed(3)}
            </span>
            <span className="score-label">Predicted MAS Performance</span>
          </div>
          <div className="score-description">
            <p>
              This score represents the overall predicted Multi-Agent System performance
              based on {Object.keys(run.features || {}).length} behavioral features analyzed by the XGBoost model.
            </p>
            {run.auto_enhanced && (
              <div className="enhancement-notice">
                ✨ This code was auto-enhanced through iterative improvement loops
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Benchmark Scores (if available) */}
      {(run.humaneval_score || run.gsm8k_score || run.mmlu_score) && (
        <div className="section-card">
          <h2>📈 Benchmark Scores</h2>
          <div className="benchmark-grid">
            {run.humaneval_score && (
              <div className="benchmark-card">
                <div className="benchmark-icon">💻</div>
                <div className="benchmark-name">HumanEval</div>
                <div className="benchmark-score">{run.humaneval_score.toFixed(2)}%</div>
              </div>
            )}
            {run.gsm8k_score && (
              <div className="benchmark-card">
                <div className="benchmark-icon">🔢</div>
                <div className="benchmark-name">GSM8K</div>
                <div className="benchmark-score">{run.gsm8k_score.toFixed(2)}%</div>
              </div>
            )}
            {run.mmlu_score && (
              <div className="benchmark-card">
                <div className="benchmark-icon">📚</div>
                <div className="benchmark-name">MMLU</div>
                <div className="benchmark-score">{run.mmlu_score.toFixed(2)}%</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* All Features */}
      <div className="section-card">
        <h2>🔧 All Features ({Object.keys(run.features || {}).length})</h2>
        <div className="features-table">
          <table>
            <thead>
              <tr>
                <th>Feature Name</th>
                <th>Value</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(run.features || {}).map(([key, value]) => (
                <tr key={key}>
                  <td className="feature-name">{key.replace(/_/g, ' ')}</td>
                  <td className="feature-value">
                    {typeof value === 'number' ? value.toFixed(4) : value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminPromptDetail;
