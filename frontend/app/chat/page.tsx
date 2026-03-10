"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Bot,
  User,
  Loader2,
  MessageSquare,
  FileSearch,
  ShieldCheck,
  AlertTriangle,
} from "lucide-react";

import AppLayout from "@/components/AppLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import {
  useChatMessages,
  chatKeys,
  type ChatMessage,
  type Source,
} from "@/lib/api/chat";
import { useStreamingChat } from "@/lib/hooks/useStreamingChat";

import ChatSidebar from "./components/ChatSidebar";
import DocumentPreview from "./components/DocumentPreview";

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function confidenceLabel(score: number): {
  label: string;
  variant: "success" | "warning" | "destructive";
  Icon: React.ElementType;
} {
  if (score >= 0.7) {
    return { label: "Hohe Konfidenz", variant: "success", Icon: ShieldCheck };
  }
  if (score >= 0.4) {
    return {
      label: "Mittlere Konfidenz",
      variant: "warning",
      Icon: AlertTriangle,
    };
  }
  return {
    label: "Niedrige Konfidenz",
    variant: "destructive",
    Icon: AlertTriangle,
  };
}

/* ------------------------------------------------------------------ */
/* Source Badge                                                         */
/* ------------------------------------------------------------------ */

function SourceBadge({
  source,
  index,
  onClick,
}: {
  source: Source;
  index: number;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-1 rounded-full border border-accent/20 bg-accent/5 px-2 py-0.5 text-xs font-medium text-accent transition-colors hover:bg-accent/10"
      title={source.document_name}
    >
      <FileSearch className="h-3 w-3" />
      <span>[{index + 1}]</span>
      <span className="max-w-[120px] truncate">{source.document_name}</span>
    </button>
  );
}

/* ------------------------------------------------------------------ */
/* Message Bubble                                                      */
/* ------------------------------------------------------------------ */

function MessageBubble({
  message,
  onSourceClick,
}: {
  message: {
    role: "user" | "assistant";
    content: string;
    sources?: Source[];
    created_at?: string;
  };
  onSourceClick: (source: Source) => void;
}) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 ${isUser ? "justify-end" : "flex-row"}`}
    >
      {/* Avatar — only for assistant */}
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
          <Bot className="h-4 w-4" />
        </div>
      )}

      {/* Content */}
      <div
        className={`flex max-w-[85%] flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}
      >
        <div
          className={`rounded-lg px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "border border-border bg-surface-raised text-primary shadow-card"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-code:rounded prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:text-xs prose-pre:bg-surface-sunken prose-pre:text-xs">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {message.sources.map((src, idx) => (
              <SourceBadge
                key={`${src.document_name}-${idx}`}
                source={src}
                index={idx}
                onClick={() => onSourceClick(src)}
              />
            ))}
          </div>
        )}

        {/* Timestamp */}
        {message.created_at && (
          <span className="text-[10px] text-muted-foreground/60">
            {formatTime(message.created_at)}
          </span>
        )}
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Streaming Bubble                                                    */
/* ------------------------------------------------------------------ */

function StreamingBubble({
  text,
  sources,
  confidence,
  isStreaming,
  onSourceClick,
}: {
  text: string;
  sources: Source[];
  confidence: number | null;
  isStreaming: boolean;
  onSourceClick: (source: Source) => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      {/* Avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
        <Bot className="h-4 w-4" />
      </div>

      {/* Content */}
      <div className="flex max-w-[85%] flex-col gap-1.5">
        <div className="rounded-lg border border-border bg-surface-raised px-4 py-3 text-sm leading-relaxed text-primary shadow-card">
          {text ? (
            <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-code:rounded prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:text-xs prose-pre:bg-surface-sunken prose-pre:text-xs">
              <ReactMarkdown>{text}</ReactMarkdown>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Antwort wird generiert...</span>
            </div>
          )}

          {/* Streaming cursor */}
          {isStreaming && text && (
            <span className="inline-block h-4 w-1.5 animate-pulse rounded-sm bg-accent/60" />
          )}
        </div>

        {/* Sources */}
        {sources.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {sources.map((src, idx) => (
              <SourceBadge
                key={`${src.document_name}-${idx}`}
                source={src}
                index={idx}
                onClick={() => onSourceClick(src)}
              />
            ))}
          </div>
        )}

        {/* Confidence */}
        {confidence !== null && !isStreaming && (
          <div>
            {(() => {
              const c = confidenceLabel(confidence);
              return (
                <Badge variant={c.variant} className="gap-1">
                  <c.Icon className="h-3 w-3" />
                  {c.label} ({Math.round(confidence * 100)}%)
                </Badge>
              );
            })()}
          </div>
        )}
      </div>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Empty State                                                         */
/* ------------------------------------------------------------------ */

function EmptyState() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent/10">
        <MessageSquare className="h-8 w-8 text-accent" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-primary">
          Streamworks Hilfe
        </h2>
        <p className="mt-1 max-w-md text-sm text-muted-foreground">
          Stellen Sie Fragen zur Streamworks-Dokumentation. Der Assistent
          durchsucht die Wissensbasis und liefert quellenbasierte Antworten.
        </p>
      </div>
      <div className="mt-2 flex flex-wrap justify-center gap-2">
        {[
          "Was sind die wichtigsten Parameter?",
          "Erklaere den Dateitransfer-Prozess.",
          "Welche Fehlerbehandlung ist vorgesehen?",
        ].map((suggestion) => (
          <span
            key={suggestion}
            className="rounded-full border border-border bg-surface-raised px-3 py-1.5 text-xs text-muted-foreground"
          >
            {suggestion}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Chat Page                                                      */
/* ------------------------------------------------------------------ */

export default function ChatPage() {
  const queryClient = useQueryClient();
  const toast = useToast();

  // Session state
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  // Source preview
  const [previewSource, setPreviewSource] = useState<Source | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  // Input
  const [inputValue, setInputValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Streaming
  const streaming = useStreamingChat();

  // Persisted messages for the active session
  const { data: persistedMessages = [] } = useChatMessages(activeSessionId);

  // Build display messages: persisted + current streaming if active
  const displayMessages: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    sources?: Source[];
    created_at?: string;
  }> = [...persistedMessages];

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [displayMessages.length, streaming.streamedText, scrollToBottom]);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [inputValue]);

  // Handlers
  async function handleSend() {
    const msg = inputValue.trim();
    if (!msg || streaming.isStreaming) return;

    setInputValue("");
    streaming.reset();

    // Optimistically add user message to display
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: activeSessionId ?? "",
      role: "user",
      content: msg,
      created_at: new Date().toISOString(),
    };

    // We add it to the query cache temporarily
    if (activeSessionId) {
      queryClient.setQueryData<ChatMessage[]>(
        chatKeys.messages(activeSessionId),
        (old) => [...(old ?? []), tempUserMsg]
      );
    }

    const result = await streaming.sendMessage(msg, activeSessionId);

    // After streaming completes, update the session ID and invalidate queries
    const newSessionId = result.sessionId ?? activeSessionId;
    if (newSessionId && newSessionId !== activeSessionId) {
      setActiveSessionId(newSessionId);
    }

    // Give the backend a moment to persist, then refresh
    setTimeout(() => {
      queryClient.invalidateQueries({ queryKey: chatKeys.sessions });
      if (newSessionId) {
        queryClient.invalidateQueries({
          queryKey: chatKeys.messages(newSessionId),
        });
      }
    }, 500);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleNewChat() {
    setActiveSessionId(null);
    streaming.reset();
    setInputValue("");
  }

  function handleSelectSession(sessionId: string) {
    if (streaming.isStreaming) return;
    streaming.reset();
    setActiveSessionId(sessionId);
  }

  function handleSourceClick(source: Source) {
    setPreviewSource(source);
    setPreviewOpen(true);
  }

  // Determine whether to show the streaming bubble
  const showStreamingBubble =
    streaming.isStreaming || streaming.streamedText.length > 0;

  // Check if the streaming bubble content is already in persisted messages
  // (happens after invalidation). If so, don't show streaming bubble.
  const lastPersisted = persistedMessages[persistedMessages.length - 1];
  const streamingAlreadyPersisted =
    !streaming.isStreaming &&
    lastPersisted?.role === "assistant" &&
    streaming.streamedText.length > 0 &&
    lastPersisted.content.length >= streaming.streamedText.length * 0.8;

  const shouldShowStreamingBubble =
    showStreamingBubble && !streamingAlreadyPersisted;

  const hasMessages = displayMessages.length > 0 || shouldShowStreamingBubble;

  return (
    <AppLayout noScroll>
      <div className="flex h-full pt-1">
        {/* Sidebar */}
        <ChatSidebar
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
        />

        {/* Main chat area */}
        <div className="flex flex-1 flex-col bg-surface-raised">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto scrollbar-thin">
            {!hasMessages ? (
              <EmptyState />
            ) : (
              <div className="mx-auto w-full max-w-4xl space-y-6 px-4 py-6">
                <AnimatePresence initial={false}>
                  {displayMessages.map((msg) => (
                    <MessageBubble
                      key={msg.id}
                      message={msg}
                      onSourceClick={handleSourceClick}
                    />
                  ))}
                </AnimatePresence>

                {/* Streaming response */}
                {shouldShowStreamingBubble && (
                  <StreamingBubble
                    text={streaming.streamedText}
                    sources={streaming.sources}
                    confidence={streaming.confidence}
                    isStreaming={streaming.isStreaming}
                    onSourceClick={handleSourceClick}
                  />
                )}

                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input bar */}
          <div className="border-t border-border bg-surface-raised px-4 py-3">
            <div className="mx-auto flex w-full max-w-5xl items-end gap-3">
              <div className="relative flex-1">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Stellen Sie eine Frage zu Ihren Dokumenten..."
                  rows={1}
                  disabled={streaming.isStreaming}
                  className="w-full resize-none rounded-lg border border-border bg-surface px-4 py-2.5 pr-12 text-sm text-primary shadow-sm transition-colors placeholder:text-muted-foreground focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/20 disabled:opacity-50"
                />
              </div>
              <Button
                onClick={handleSend}
                disabled={!inputValue.trim() || streaming.isStreaming}
                size="icon"
                className="h-10 w-10 shrink-0"
              >
                {streaming.isStreaming ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="mx-auto mt-1.5 max-w-5xl text-center text-[10px] text-muted-foreground/60">
              KI-generierte Antworten koennen Fehler enthalten. Quellen pruefen.
            </p>
          </div>
        </div>
      </div>

      {/* Document preview modal */}
      <DocumentPreview
        source={previewSource}
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
      />
    </AppLayout>
  );
}
