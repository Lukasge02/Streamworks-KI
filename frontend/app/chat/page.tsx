"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import AppLayout from "../components/AppLayout";
import ChatSessionSidebar, {
  ChatSessionSidebarRef,
} from "./components/ChatSessionSidebar";
import DocumentPreviewModal from "./components/DocumentPreviewModal";
import { useChatSession, type Source } from "../../lib/api/chat";
import { useStreamingChat, type StreamSource } from "../../lib/hooks/useStreamingChat";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  timestamp: Date;
  confidence?: number;
  confidence_level?: string;
  query_type?: string;
  warnings?: string[];
  isStreaming?: boolean;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [showSources, setShowSources] = useState<number | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [previewDoc, setPreviewDoc] = useState<{
    docId: string;
    filename: string;
    content: string;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sidebarRef = useRef<ChatSessionSidebarRef>(null);

  // TanStack Query hooks
  const { data: sessionData } = useChatSession(activeSessionId);

  // Streaming hook
  const {
    isStreaming,
    currentText,
    sources: streamSources,
    status,
    confidence,
    queryType,
    streamQuery,
    cancelStream,
    error: streamError,
  } = useStreamingChat();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentText]);

  // Load session messages when session data changes
  useEffect(() => {
    if (sessionData?.messages) {
      const loadedMessages: Message[] = sessionData.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        sources: msg.sources || [],
        timestamp: new Date(msg.created_at || Date.now()),
      }));
      setMessages(loadedMessages);
    }
  }, [sessionData]);

  // Send message with streaming
  const sendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    // Stream the response
    streamQuery(
      userMessage.content,
      5,
      activeSessionId,
      (fullResponse: string, sources: StreamSource[], newSessionId: string | null) => {
        // When streaming completes, update session and add final message
        if (newSessionId && !activeSessionId) {
          setActiveSessionId(newSessionId);
          setTimeout(() => {
            sidebarRef.current?.refreshSessions();
          }, 500);
        }

        // Convert StreamSource to Source format
        const formattedSources: Source[] = sources.map((s, i) => ({
          doc_id: s.doc_id,
          filename: s.filename,
          content: s.content,
          score: s.score,
          doc_type: s.filename?.split('.').pop() || 'unknown',
          index: i + 1,
        }));

        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: fullResponse,
            sources: formattedSources,
            timestamp: new Date(),
            confidence: confidence || undefined,
            query_type: queryType || undefined,
          },
        ]);
      }
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setActiveSessionId(null);
    setShowSources(null);
    cancelStream();
  };

  const handleSessionSelect = (sessionId: string) => {
    if (sessionId !== activeSessionId) {
      setActiveSessionId(sessionId);
      setShowSources(null);
      cancelStream();
    }
  };

  // Custom markdown components for styling
  const MarkdownContent = ({ content }: { content: string }) => (
    <ReactMarkdown
      components={{
        // Bold text
        strong: ({ children }) => (
          <strong className="font-semibold">{children}</strong>
        ),
        // Italic text
        em: ({ children }) => (
          <em className="italic">{children}</em>
        ),
        // Code blocks
        code: ({ children, className }) => {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded text-xs font-mono">
                {children}
              </code>
            );
          }
          return (
            <code className="block bg-slate-900 text-slate-100 p-3 rounded-lg text-xs font-mono overflow-x-auto my-2">
              {children}
            </code>
          );
        },
        // Lists
        ul: ({ children }) => (
          <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="text-sm">{children}</li>
        ),
        // Paragraphs
        p: ({ children }) => (
          <p className="mb-2 last:mb-0">{children}</p>
        ),
        // Headers
        h1: ({ children }) => (
          <h1 className="text-lg font-bold mt-3 mb-2">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-bold mt-3 mb-2">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-bold mt-2 mb-1">{children}</h3>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-80px)] overflow-hidden -m-6">
        {/* Sidebar Toggle Button (mobile) */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden fixed top-20 left-4 z-50 p-2 bg-white rounded-lg shadow-lg border border-slate-200"
        >
          <svg
            className="w-5 h-5 text-slate-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        {/* Session Sidebar */}
        <div className={`${sidebarOpen ? "block" : "hidden"} lg:block`}>
          <ChatSessionSidebar
            ref={sidebarRef}
            activeSessionId={activeSessionId}
            onSessionSelect={handleSessionSelect}
            onNewChat={handleNewChat}
          />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col p-4 pb-6 bg-slate-50/30 min-h-0">
          {/* Page Header */}
          <div className="flex items-center justify-between mb-4 flex-shrink-0">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Dokumente-Chat
              </h1>
              <p className="text-sm text-slate-500">
                RAG-basierte Fragen an Ihre Wissensbasis
              </p>
            </div>
            <div className="flex items-center gap-2">
              {activeSessionId && !isStreaming && (
                <div className="flex items-center gap-1.5 text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded-full border border-green-200">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                  Session aktiv
                </div>
              )}
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-auto bg-white rounded-2xl border border-slate-200 mb-3 shadow-sm min-h-0">
            <div className="p-6 space-y-6">
              {messages.length === 0 && !isStreaming ? (
                <div className="text-center py-16">
                  <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/10">
                    <svg
                      className="w-10 h-10 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                      />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 mb-2">
                    Fragen Sie Ihre Dokumente
                  </h2>
                  <p className="text-slate-500 mb-8 max-w-md mx-auto text-sm">
                    Die KI durchsucht Ihre Wissensbasis und antwortet basierend
                    auf den hochgeladenen Dokumenten.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
                    {[
                      "Was ist Streamworks?",
                      "Welche Job-Typen gibt es?",
                      "Wie funktioniert ein FileTransfer?",
                      "Was ist ein Agent?",
                    ].map((s, i) => (
                      <button
                        key={i}
                        onClick={() => setInput(s)}
                        className="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-600 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50/50 transition-all shadow-sm"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {message.role === "assistant" && (
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/20">
                          <svg
                            className="w-5 h-5 text-white"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                            />
                          </svg>
                        </div>
                      )}
                      <div
                        className={`max-w-[75%] ${message.role === "user" ? "order-1" : ""}`}
                      >
                        <div
                          className={`rounded-2xl px-4 py-3 ${message.role === "user"
                            ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/20"
                            : "bg-slate-100 text-slate-800"
                            }`}
                        >
                          <div className="text-sm leading-relaxed prose prose-sm max-w-none prose-slate">
                            {message.role === "assistant" ? (
                              <MarkdownContent content={message.content} />
                            ) : (
                              <p className="whitespace-pre-wrap">{message.content}</p>
                            )}
                          </div>

                          <div className="flex justify-between items-end mt-1.5 pt-2 border-t border-slate-200/50">
                            <div className="flex gap-2">
                              {message.role === "assistant" &&
                                message.confidence !== undefined && (
                                  <span
                                    className={`text-[10px] font-medium px-1.5 py-0.5 rounded-md border ${message.confidence > 0.8
                                      ? "bg-green-50 text-green-600 border-green-100"
                                      : message.confidence > 0.5
                                        ? "bg-yellow-50 text-yellow-600 border-yellow-100"
                                        : "bg-red-50 text-red-600 border-red-100"
                                      }`}
                                    title={message.confidence_level}
                                  >
                                    {(message.confidence * 100).toFixed(0)}%
                                  </span>
                                )}
                            </div>
                            <span className="text-[10px] text-slate-400">
                              {message.timestamp.toLocaleTimeString("de-DE", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          </div>
                        </div>

                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-2 text-right">
                            <button
                              onClick={() =>
                                setShowSources(
                                  showSources === index ? null : index
                                )
                              }
                              className="text-xs text-slate-400 hover:text-blue-600 inline-flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-slate-100 transition-colors ml-auto"
                            >
                              <svg
                                className="w-3.5 h-3.5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                                />
                              </svg>
                              {message.sources.length} Quellen
                            </button>

                            {showSources === index && (
                              <div className="mt-2 space-y-2 text-left">
                                {message.sources.map((source, sIndex) => (
                                  <div
                                    key={sIndex}
                                    className="bg-slate-50 rounded-xl p-3 border border-slate-200 cursor-pointer hover:bg-blue-50/50 hover:border-blue-200 transition-all group"
                                    onClick={() => {
                                      const docId = source.doc_id || source.id;
                                      if (docId) {
                                        setPreviewDoc({
                                          docId: docId,
                                          filename: source.filename || "Unknown",
                                          content: source.content,
                                        });
                                      }
                                    }}
                                  >
                                    <div className="flex items-center gap-2 mb-1.5">
                                      <span className="text-xs font-bold text-slate-500 min-w-[1.5rem] group-hover:text-blue-600">
                                        [{source.index || sIndex + 1}]
                                      </span>
                                      <span className="text-xs font-medium text-blue-600 px-2 py-0.5 bg-blue-50 rounded-md ring-1 ring-blue-500/10">
                                        {source.doc_type?.toUpperCase() || 'DOC'}
                                      </span>
                                      <span
                                        className="text-xs font-medium text-slate-700 truncate flex-1 group-hover:text-blue-700"
                                        title={source.filename}
                                      >
                                        {source.filename}
                                      </span>
                                      <span className="text-xs font-medium text-slate-400 whitespace-nowrap bg-slate-100 px-1.5 py-0.5 rounded">
                                        {(source.score * 100).toFixed(0)}%
                                      </span>
                                    </div>
                                    <p className="text-xs text-slate-600 line-clamp-2 group-hover:text-slate-800">
                                      {source.content}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                      {message.role === "user" && (
                        <div className="w-10 h-10 bg-slate-200 rounded-xl flex items-center justify-center flex-shrink-0">
                          <svg
                            className="w-5 h-5 text-slate-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                            />
                          </svg>
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Streaming Message */}
                  {isStreaming && (
                    <div className="flex gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/20">
                        <svg
                          className="w-5 h-5 text-white"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                          />
                        </svg>
                      </div>
                      <div className="max-w-[75%]">
                        {/* Streaming text */}
                        {currentText && (
                          <div className="bg-slate-100 rounded-2xl px-4 py-3">
                            <div className="text-sm leading-relaxed prose prose-sm max-w-none prose-slate">
                              <MarkdownContent content={currentText} />
                              <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-0.5"></span>
                            </div>
                          </div>
                        )}

                        {/* Sources preview while streaming */}
                        {streamSources.length > 0 && !currentText && (
                          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
                            <div className="text-xs font-medium text-slate-500 mb-2">
                              📚 {streamSources.length} Quellen gefunden
                            </div>
                            {streamSources.slice(0, 2).map((source, i) => (
                              <div key={i} className="text-xs text-slate-600 truncate">
                                • {source.filename}
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Sources preview while streaming */}
                        {streamSources.length > 0 && !currentText && (
                          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200 mb-2">
                            <div className="text-xs font-medium text-slate-500 mb-2">
                              📚 {streamSources.length} Quellen gefunden
                            </div>
                            {streamSources.slice(0, 2).map((source, i) => (
                              <div key={i} className="text-xs text-slate-600 truncate">
                                • {source.filename}
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Loading dots or Status when no text yet */}
                        {!currentText && streamSources.length === 0 && (
                          <div className="bg-slate-100 rounded-2xl px-5 py-4">
                            {status ? (
                              <div className="flex items-center gap-2.5">
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium text-slate-500 animate-pulse">{status}</span>
                              </div>
                            ) : (
                              <div className="flex gap-1.5">
                                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                                <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Error message */}
                  {streamError && (
                    <div className="flex gap-3">
                      <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div className="bg-red-50 rounded-2xl px-4 py-3 border border-red-100">
                        <p className="text-sm text-red-600">{streamError}</p>
                      </div>
                    </div>
                  )}
                </>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <div className="flex gap-3 flex-shrink-0">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Stellen Sie eine Frage zu Ihren Dokumenten..."
                rows={1}
                disabled={isStreaming}
                className="w-full px-5 py-3.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-slate-800 bg-white shadow-sm pr-12 disabled:bg-slate-50 disabled:text-slate-400"
                style={{ minHeight: "52px", maxHeight: "120px" }}
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">
                ⏎
              </div>
            </div>
            {isStreaming ? (
              <button
                onClick={cancelStream}
                className="px-5 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl font-medium transition-all border border-slate-200 flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10h6v4H9z" />
                </svg>
                Stop
              </button>
            ) : (
              <button
                onClick={sendMessage}
                disabled={!input.trim()}
                className="px-6 py-3.5 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
                Senden
              </button>
            )}
          </div>
        </div>

        {/* Document Preview Modal */}
        <DocumentPreviewModal
          isOpen={!!previewDoc}
          onClose={() => setPreviewDoc(null)}
          docId={previewDoc?.docId || ""}
          filename={previewDoc?.filename || ""}
          initialContent={previewDoc?.content}
        />
      </div>
    </AppLayout>
  );
}
