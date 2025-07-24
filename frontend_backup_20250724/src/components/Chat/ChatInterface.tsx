import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useChat } from '../../hooks/useChat';

export const ChatInterface: React.FC = () => {
  const { messages, isLoading, sendMessage, addMessage } = useChat();

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <MessageList messages={messages} isLoading={isLoading} />
      <ChatInput onSendMessage={sendMessage} onFileUpload={addMessage} />
    </div>
  );
};