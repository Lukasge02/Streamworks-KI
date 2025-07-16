import { MessageType } from '../types';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  type?: MessageType;
  metadata?: {
    sources?: string[];
    confidence?: number;
    processing_time?: number;
  };
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  lastUpdated: Date;
}

const STORAGE_KEY = 'streamworks_chat_sessions';
const CURRENT_SESSION_KEY = 'streamworks_current_session';

export class ChatStorage {
  static saveChatSession(session: ChatSession): void {
    try {
      const sessions = this.getAllSessions();
      const existingIndex = sessions.findIndex(s => s.id === session.id);
      
      if (existingIndex >= 0) {
        sessions[existingIndex] = session;
      } else {
        sessions.push(session);
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch (error) {
      console.error('Failed to save chat session:', error);
    }
  }

  static getAllSessions(): ChatSession[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return [];
      
      const sessions = JSON.parse(stored);
      return sessions.map((session: any) => ({
        ...session,
        createdAt: new Date(session.createdAt),
        lastUpdated: new Date(session.lastUpdated),
        messages: session.messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      }));
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
      return [];
    }
  }

  static getSessionById(id: string): ChatSession | null {
    const sessions = this.getAllSessions();
    return sessions.find(session => session.id === id) || null;
  }

  static deleteSession(id: string): void {
    try {
      const sessions = this.getAllSessions();
      const filtered = sessions.filter(session => session.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete chat session:', error);
    }
  }

  static clearAllSessions(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(CURRENT_SESSION_KEY);
    } catch (error) {
      console.error('Failed to clear chat sessions:', error);
    }
  }

  static setCurrentSession(sessionId: string): void {
    try {
      localStorage.setItem(CURRENT_SESSION_KEY, sessionId);
    } catch (error) {
      console.error('Failed to set current session:', error);
    }
  }

  static getCurrentSession(): string | null {
    try {
      return localStorage.getItem(CURRENT_SESSION_KEY);
    } catch (error) {
      console.error('Failed to get current session:', error);
      return null;
    }
  }

  static createNewSession(title?: string): ChatSession {
    const session: ChatSession = {
      id: crypto.randomUUID(),
      title: title || 'Neue Konversation',
      messages: [],
      createdAt: new Date(),
      lastUpdated: new Date()
    };
    
    this.saveChatSession(session);
    this.setCurrentSession(session.id);
    
    return session;
  }

  static generateTitle(messages: ChatMessage[]): string {
    const firstUserMessage = messages.find(msg => msg.sender === 'user');
    if (firstUserMessage) {
      const title = firstUserMessage.text.slice(0, 50);
      return title.length < firstUserMessage.text.length ? title + '...' : title;
    }
    return 'Neue Konversation';
  }

  static updateSessionTitle(sessionId: string, title: string): void {
    const session = this.getSessionById(sessionId);
    if (session) {
      session.title = title;
      session.lastUpdated = new Date();
      this.saveChatSession(session);
    }
  }

  static addMessageToSession(sessionId: string, message: ChatMessage): void {
    const session = this.getSessionById(sessionId);
    if (session) {
      session.messages.push(message);
      session.lastUpdated = new Date();
      
      // Auto-generate title from first message if it's still default
      if (session.title === 'Neue Konversation' && session.messages.length === 1) {
        session.title = this.generateTitle(session.messages);
      }
      
      this.saveChatSession(session);
    }
  }
}