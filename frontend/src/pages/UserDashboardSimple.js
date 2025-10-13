import React, { useState, useEffect, useRef } from 'react';
import { runMAS, getUserRuns } from '../api';
import './UserDashboardSimple.css';

function UserDashboardSimple({ user, onLogout }) {
  const [messages, setMessages] = useState([
    { 
      type: 'assistant', 
      text: '👋 Hi! I\'m your AI coding assistant powered by Multi-Agent System. Just describe what you want to code, and I\'ll generate it for you!',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedMetrics, setExpandedMetrics] = useState({});
  const [recentRuns, setRecentRuns] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadRecentRuns();
  }, []);

  const loadRecentRuns = async () => {
    try {
      const runs = await getUserRuns();
      setRecentRuns(runs);
    } catch (error) {
      console.error('Failed to load recent runs:', error);
    }
  };

  const startNewChat = () => {
    setMessages([
      { 
        type: 'assistant', 
        text: '👋 Hi! I\'m your AI coding assistant. What would you like to code today?',
        timestamp: new Date()
      }
    ]);
    setCurrentConversationId(null);
    setExpandedMetrics({});
  };

  const loadConversation = (run) => {
    setMessages([
      { 
        type: 'assistant', 
        text: '📂 Previous conversation loaded.',
        timestamp: new Date(run.created_at)
      },
      {
        type: 'user',
        text: run.task,
        timestamp: new Date(run.created_at)
      },
      {
        type: 'assistant',
        text: '✅ Here\'s your code:',
        code: run.code,
        metrics: {
          predicted_score: run.predicted_score,
          features: run.features,
          run_id: run._id
        },
        timestamp: new Date(run.created_at)
      }
    ]);
    setCurrentConversationId(run._id);
    setSidebarOpen(false); // Close sidebar on mobile
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage = inputText.trim();
    setInputText('');

    // Add user message
    const userMsg = {
      type: 'user',
      text: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      // Call MAS API
      const response = await runMAS(userMessage, '');
      
      // Add assistant response with code and metrics
      const assistantMsg = {
        type: 'assistant',
        text: '✅ Here\'s your code:',
        code: response.code || response.result || 'No code generated',
        metrics: {
          predicted_score: response.predicted_score,
          features: response.features,
          auto_enhanced: response.auto_enhanced,
          run_id: response.run_id
        },
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMsg]);
      
      // Reload recent runs to include this new one
      loadRecentRuns();
      
    } catch (error) {
      // Add error message
      const errorMsg = {
        type: 'assistant',
        text: `❌ Sorry, something went wrong: ${error.message}`,
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleMetrics = (index) => {
    setExpandedMetrics(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="simple-dashboard">
      {/* Sidebar Toggle Button (Mobile) */}
      <button 
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        title="Toggle History"
      >
        ☰
      </button>

      {/* History Sidebar */}
      <div className={`history-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h3>💬 Chat History</h3>
          <button 
            className="new-chat-button"
            onClick={startNewChat}
          >
            + New Chat
          </button>
        </div>
        
        <div className="recent-runs">
          {recentRuns.length === 0 ? (
            <p className="no-history">No previous conversations</p>
          ) : (
            recentRuns.map((run, idx) => (
              <div 
                key={run._id || idx}
                className={`history-item ${currentConversationId === run._id ? 'active' : ''}`}
                onClick={() => loadConversation(run)}
              >
                <div className="history-title">
                  {run.task?.substring(0, 50) || 'Untitled'}
                  {run.task?.length > 50 && '...'}
                </div>
                <div className="history-meta">
                  <span className="history-score">
                    ⭐ {run.predicted_score?.toFixed(2) || 'N/A'}
                  </span>
                  <span className="history-date">
                    {new Date(run.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-chat-area">
        {/* Header */}
        <header className="simple-header">
        <div className="header-content">
          <h1>🤖 AI Code Assistant</h1>
          <div className="user-section">
            <span className="username">👤 {user.username}</span>
            <button onClick={onLogout} className="logout-button">Logout</button>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages-area">
          {messages.map((msg, index) => (
            <div key={index} className={`message-wrapper ${msg.type}`}>
              <div className="message-bubble">
                {/* Message Text */}
                <div className="message-text">{msg.text}</div>

                {/* Code Block (if present) */}
                {msg.code && (
                  <div className="code-block">
                    <div className="code-header">
                      <span>💻 Generated Code</span>
                      {msg.metrics && (
                        <span className="score-badge">
                          Score: {msg.metrics.predicted_score.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <pre className="code-content">{msg.code}</pre>
                    
                    {/* Metrics Toggle */}
                    {msg.metrics && (
                      <button 
                        className="metrics-toggle"
                        onClick={() => toggleMetrics(index)}
                      >
                        {expandedMetrics[index] ? '📊 Hide Metrics' : '📊 Show Metrics'}
                      </button>
                    )}
                  </div>
                )}

                {/* Collapsible Metrics Panel */}
                {msg.metrics && expandedMetrics[index] && (
                  <div className="metrics-panel">
                    <h4>📈 Performance Metrics</h4>
                    
                    <div className="metrics-grid">
                      <div className="metric-item">
                        <div className="metric-label">Final Score</div>
                        <div className="metric-value highlight">
                          {msg.metrics.predicted_score.toFixed(4)}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Avg Personal Score</div>
                        <div className="metric-value">
                          {msg.metrics.features?.avg_personal_score?.toFixed(4) || 'N/A'}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Min Personal Score</div>
                        <div className="metric-value">
                          {msg.metrics.features?.min_personal_score?.toFixed(4) || 'N/A'}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Enhancement Loops</div>
                        <div className="metric-value">
                          {msg.metrics.features?.max_loops || 0}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Total Latency</div>
                        <div className="metric-value">
                          {msg.metrics.features?.total_latency?.toFixed(2) || '0'}s
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Token Usage</div>
                        <div className="metric-value">
                          {msg.metrics.features?.total_token_usage || 0}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Agents Used</div>
                        <div className="metric-value">
                          {msg.metrics.features?.num_nodes || 0}
                        </div>
                      </div>
                      
                      <div className="metric-item">
                        <div className="metric-label">Agent Interactions</div>
                        <div className="metric-value">
                          {msg.metrics.features?.num_edges || 0}
                        </div>
                      </div>
                    </div>
                    
                    {msg.metrics.auto_enhanced && (
                      <div className="enhancement-badge">
                        ✨ Auto-Enhanced for Better Quality
                      </div>
                    )}
                  </div>
                )}

                {/* Timestamp */}
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {/* Loading Indicator */}
          {loading && (
            <div className="message-wrapper assistant">
              <div className="message-bubble">
                <div className="loading-indicator">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <span>Generating code...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe what you want to code... (e.g., 'Create a function to sort an array')"
            disabled={loading}
            rows="3"
          />
          <button 
            onClick={handleSendMessage}
            disabled={loading || !inputText.trim()}
            className="send-button"
          >
            {loading ? '⏳' : '🚀 Generate'}
          </button>
        </div>
      </div>
    </div>
    </div>
  );
}

export default UserDashboardSimple;
