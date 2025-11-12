import React, { createContext, useContext, useState, useEffect } from 'react';

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [conversations, setConversations] = useState(() => {
    try {
      const raw = localStorage.getItem("am_conversations");
      return raw ? JSON.parse(raw) : {};
    } catch {
      return {};
    }
  });
  const [currentConversationId, setCurrentConversationId] = useState(() => {
    try {
      return localStorage.getItem("am_currentConversationId") || null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    localStorage.setItem("am_conversations", JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    if (currentConversationId)
      localStorage.setItem("am_currentConversationId", currentConversationId);
    else
      localStorage.removeItem("am_currentConversationId");
  }, [currentConversationId]);

  const createConversationIfMissing = (id) => {
    if (!id) return;
    setConversations(prev => {
      if (prev[id]) return prev;
      return {
        ...prev,
        [id]: { id, messages: [{ type: 'bot', text: "Hello! I'm your AgentMonitor assistant. Describe your coding task and I'll run the Multi-Agent System to help you!" }], metadata: {} }
      };
    });
  };

  const appendMessage = (conversationId, msg) => {
    setConversations(prev => {
      if (!conversationId) return prev;
      const conv = prev[conversationId] || { id: conversationId, messages: [] };
      return { ...prev, [conversationId]: { ...conv, messages: [...conv.messages, msg] } };
    });
  };

  const setConversation = (conversationId, convObj) => {
    setConversations(prev => ({ ...prev, [conversationId]: convObj }));
  };

  const value = {
    conversations,
    currentConversationId,
    setCurrentConversationId,
    createConversationIfMissing,
    appendMessage,
    setConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
}