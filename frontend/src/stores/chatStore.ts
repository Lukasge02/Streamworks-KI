/**
 * Chat Store - Manages chat messages, conversations, and streaming state
 */

import { create } from 'zustand';
import { subscribeWithSelector, devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { 
  ChatMessage, 
  Conversation, 
  StreamingChatResponse,
  ChatRequest 
} from '../types/api';
import { streamWorksAPI } from '../services/api';

interface ChatStore {
  // State
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Record<string, ChatMessage[]>;
  streamingMessage: {
    conversationId: string;
    tokens: string[];
    isStreaming: boolean;
    sources?: string[];
  } | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setCurrentConversation: (conversationId: string | null) => void;
  createConversation: (title: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  loadMessages: (conversationId: string) => Promise<void>;
  sendMessage: (request: ChatRequest) => Promise<void>;
  startStreaming: (conversationId: string) => void;
  addStreamToken: (token: string) => void;
  finishStreaming: (message: ChatMessage) => void;
  stopStreaming: () => void;
  clearError: () => void;
  exportConversation: (conversationId: string, format?: 'json' | 'txt' | 'pdf') => Promise<void>;
}

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          // Initial state
          conversations: [],
          currentConversationId: null,
          messages: {},
          streamingMessage: null,
          isLoading: false,
          error: null,

          // Actions
          setCurrentConversation: (conversationId) => {
            set((state) => {
              state.currentConversationId = conversationId;
            });
          },

          createConversation: async (title) => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await streamWorksAPI.createConversation(title);
              const newConversation = response.data;

              set((state) => {
                state.conversations.unshift(newConversation);
                state.currentConversationId = newConversation.id;
                state.messages[newConversation.id] = [];
                state.isLoading = false;
              });
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to create conversation';
                state.isLoading = false;
              });
            }
          },

          deleteConversation: async (conversationId) => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              await streamWorksAPI.deleteConversation(conversationId);

              set((state) => {
                state.conversations = state.conversations.filter(c => c.id !== conversationId);
                delete state.messages[conversationId];
                
                if (state.currentConversationId === conversationId) {
                  state.currentConversationId = state.conversations[0]?.id || null;
                }
                
                state.isLoading = false;
              });
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to delete conversation';
                state.isLoading = false;
              });
            }
          },

          loadConversations: async () => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await streamWorksAPI.getConversations();
              
              set((state) => {
                state.conversations = response.items;
                state.isLoading = false;
                
                // Set current conversation if none selected
                if (!state.currentConversationId && response.items.length > 0) {
                  state.currentConversationId = response.items[0].id;
                }
              });
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to load conversations';
                state.isLoading = false;
              });
            }
          },

          loadMessages: async (conversationId) => {
            // Don't reload if already loaded
            if (get().messages[conversationId]) {
              return;
            }

            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await streamWorksAPI.getChatHistory(conversationId);
              
              set((state) => {
                state.messages[conversationId] = response.items;
                state.isLoading = false;
              });
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to load messages';
                state.isLoading = false;
              });
            }
          },

          sendMessage: async (request) => {
            const conversationId = request.conversation_id || get().currentConversationId;
            if (!conversationId) {
              throw new Error('No conversation selected');
            }

            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              // Use streaming for better UX
              get().startStreaming(conversationId);
              
              await streamWorksAPI.streamChat(
                { ...request, conversation_id: conversationId },
                (token) => {
                  get().addStreamToken(token.token);
                },
                (message) => {
                  get().finishStreaming(message);
                },
                (error) => {
                  set((state) => {
                    state.error = error.message;
                    state.isLoading = false;
                    state.streamingMessage = null;
                  });
                }
              );
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to send message';
                state.isLoading = false;
                state.streamingMessage = null;
              });
            }
          },

          startStreaming: (conversationId) => {
            set((state) => {
              state.streamingMessage = {
                conversationId,
                tokens: [],
                isStreaming: true,
                sources: undefined,
              };
            });
          },

          addStreamToken: (token) => {
            set((state) => {
              if (state.streamingMessage) {
                state.streamingMessage.tokens.push(token);
              }
            });
          },

          finishStreaming: (message) => {
            set((state) => {
              if (state.streamingMessage) {
                const conversationId = state.streamingMessage.conversationId;
                
                // Add completed message to conversation
                if (!state.messages[conversationId]) {
                  state.messages[conversationId] = [];
                }
                state.messages[conversationId].push(message);
                
                // Update conversation in list
                const convIndex = state.conversations.findIndex(c => c.id === conversationId);
                if (convIndex !== -1) {
                  state.conversations[convIndex].updated_at = message.timestamp;
                  state.conversations[convIndex].message_count += 1;
                }
                
                state.streamingMessage = null;
                state.isLoading = false;
              }
            });
          },

          stopStreaming: () => {
            set((state) => {
              state.streamingMessage = null;
              state.isLoading = false;
            });
          },

          clearError: () => {
            set((state) => {
              state.error = null;
            });
          },

          exportConversation: async (conversationId, format = 'json') => {
            set((state) => {
              state.isLoading = true;
              state.error = null;
            });

            try {
              const response = await streamWorksAPI.exportConversation(conversationId, format);
              const exportData = response.data;
              
              // Trigger download if URL is provided
              if (exportData.download_url) {
                const link = document.createElement('a');
                link.href = exportData.download_url;
                link.download = `conversation_${conversationId}.${format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }
              
              set((state) => {
                state.isLoading = false;
              });
            } catch (error) {
              set((state) => {
                state.error = error instanceof Error ? error.message : 'Failed to export conversation';
                state.isLoading = false;
              });
            }
          },
        }))
      ),
      {
        name: 'streamworks-chat-store',
        partialize: (state) => ({
          conversations: state.conversations,
          currentConversationId: state.currentConversationId,
          // Don't persist messages to avoid stale data
        }),
      }
    ),
    {
      name: 'ChatStore',
    }
  )
);

// Selectors for better performance
export const useChatSelectors = {
  currentConversation: () => {
    const { conversations, currentConversationId } = useChatStore();
    return conversations.find(c => c.id === currentConversationId) || null;
  },
  
  currentMessages: () => {
    const { messages, currentConversationId } = useChatStore();
    return currentConversationId ? messages[currentConversationId] || [] : [];
  },
  
  streamingText: () => {
    const { streamingMessage } = useChatStore();
    return streamingMessage ? streamingMessage.tokens.join('') : '';
  },
  
  isCurrentlyStreaming: () => {
    const { streamingMessage } = useChatStore();
    return streamingMessage?.isStreaming || false;
  },
};