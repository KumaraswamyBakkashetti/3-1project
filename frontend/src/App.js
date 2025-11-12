import React from 'react';
import AppContent from './AppContent.orig';
import { ChatProvider } from './context/ChatContext';

export default function App() {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
}