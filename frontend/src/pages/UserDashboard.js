import React, { useState, useEffect, useRef } from 'react';
import { runMAS, runMASStart, getUserRuns, getRun } from '../api';
import './UserDashboard.css';
import { useChat } from '../context/ChatContext';

export default function UserDashboard({ user, onLogout }) {
  const { conversations, currentConversationId, setCurrentConversationId, createConversationIfMissing, appendMessage } = useChat();
  const [inputMessage, setInputMessage] = useState('');
  const [useFullMAS, setUseFullMAS] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    // create default conversation if none
    if (!currentConversationId) {
      const id = 'default';
      setCurrentConversationId(id);
      createConversationIfMissing(id);
    }
  }, [currentConversationId, setCurrentConversationId, createConversationIfMissing]);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentConversationId]);

  const handleSend = async () => {
    if (!inputMessage.trim()) return;
    const cid = currentConversationId;
    appendMessage(cid, { type: 'user', text: inputMessage });
    setInputMessage('');
    setLoading(true);
    // simulate running MAS - you can replace with actual API calls
    try {
      const startResp = await runMASStart(inputMessage, 'auto', useFullMAS);
      const runId = startResp.run_id || ('run_' + Date.now());
      const initial_code = startResp.initial_code || '/* initial code */';
      appendMessage(cid, { type: 'bot', text: '✅ Initial code generated. See result below.' });
      appendMessage(cid, { type: 'bot', text: initial_code, isCode: true });
      setLoading(false);
    } catch (e) {
      appendMessage(cid, { type: 'bot', text: 'Error running MAS: ' + (e.message || e) });
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const conv = conversations[currentConversationId] || { messages: [] };

  return (
    <div className="chatbot-dashboard">
      <header className="dashboard-header">
        <div className="header-left">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? "Show sidebar" : "Hide sidebar"}
          >
            {sidebarCollapsed ? '☰' : '✕'}
          </button>
          <h1>🤖 AgentMonitor Assistant</h1>
        </div>
        <div className="user-info">
          <span>Welcome, {user?.username || 'User'}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="main-area">
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <div className="sidebar-header">Chats</div>
          <div className="chat-list">
            {Object.values(conversations).map(c => (
              <div key={c.id} className={`chat-list-item ${c.id === currentConversationId ? 'active' : ''}`}
                   onClick={() => { setCurrentConversationId(c.id); }}>
                {c.id}
              </div>
            ))}
            <button className="new-chat-btn" onClick={() => {
              const id = 'conv_' + Date.now();
              setCurrentConversationId(id);
              createConversationIfMissing(id);
            }}>+ New Chat</button>
          </div>
        </aside>

        <section className="chat-area">
          <div className="messages-container">
            {conv.messages.map((m, i) => (
              <div key={i} className={`message ${m.type === 'user' ? 'user' : 'bot'}`}>
                {m.isCode ? <pre className="code-block">{m.text}</pre> : <div className="message-text">{m.text}</div>}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </section>
      </div>

      {/* Fixed Input Bar */}
      <div className="fixed-input-bar">
        <div className="input-inner">
          <label className="full-mas-toggle">
            <input type="checkbox" checked={useFullMAS} onChange={(e) => setUseFullMAS(e.target.checked)} />
            <span>Full MAS</span>
          </label>
          <textarea
            className="message-input"
            placeholder="Describe your coding task..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button className="send-btn" onClick={handleSend} disabled={loading}>
            {loading ? 'Running...' : 'Generate'}
          </button>
        </div>
      </div>
    </div>
  );
}