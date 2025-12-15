"use client";

import { useState, useRef, useEffect } from "react";
import {
  MessageSquare,
  Send,
  X,
  FileText,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Loader2,
} from "lucide-react";
import ReactMarkdown from "react-markdown";

const API_URL = "http://localhost:8000";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Array<{
    filename: string;
    content_snippet: string;
    score: number;
  }>;
}

interface DDDChatProps {
  projectId: string;
  projectName?: string;
  isInline?: boolean; // New: render inline instead of floating
}

export default function DDDChat({
  projectId,
  projectName,
  isInline = false,
}: DDDChatProps) {
  const [isOpen, setIsOpen] = useState(isInline); // Auto-open if inline
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [includeTestCases, setIncludeTestCases] = useState(false);
  const [expandedSources, setExpandedSources] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(
        `${API_URL}/api/testing/projects/${projectId}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: input,
            conversation_history: messages.map((m) => ({
              role: m.role,
              content: m.content,
            })),
            include_test_cases: includeTestCases,
          }),
        },
      );

      if (res.ok) {
        const data = await res.json();
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error("Chat request failed");
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Es ist ein Fehler aufgetreten. Bitte versuche es erneut.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Floating mode: show toggle button when closed
  if (!isInline && !isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-full shadow-lg shadow-indigo-500/30 transition-all hover:scale-105 z-40"
        title="DDD Chat öffnen"
      >
        <MessageSquare className="w-6 h-6" />
      </button>
    );
  }

  // Container classes based on mode
  const containerClasses = isInline
    ? "flex flex-col h-full bg-white"
    : "fixed bottom-6 right-6 w-[420px] h-[600px] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col z-50 overflow-hidden";

  return (
    <div className={containerClasses}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-gradient-to-r from-indigo-50 to-slate-50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 rounded-xl">
            <Sparkles className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-sm">
              DDD Assistent
            </h3>
            <p className="text-xs text-slate-500 truncate max-w-[200px]">
              {projectName || "Projekt"}
            </p>
          </div>
        </div>
        {!isInline && (
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-white rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <div className="p-4 bg-indigo-50 rounded-full mb-4">
              <MessageSquare className="w-8 h-8 text-indigo-400" />
            </div>
            <h4 className="font-medium text-slate-700 mb-2">
              Frag mich zum DDD
            </h4>
            <p className="text-sm text-slate-500">
              Ich beantworte Fragen basierend auf den hochgeladenen
              DDD-Dokumenten.
            </p>
            <div className="mt-4 space-y-2 text-xs text-slate-400">
              <p>Beispiel-Fragen:</p>
              <button
                onClick={() => setInput("Was sind die Hauptanforderungen?")}
                className="block w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors text-left"
              >
                "Was sind die Hauptanforderungen?"
              </button>
              <button
                onClick={() => setInput("Welche Entitäten werden beschrieben?")}
                className="block w-full px-3 py-2 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors text-left"
              >
                "Welche Entitäten werden beschrieben?"
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-md"
                  : "bg-slate-100 text-slate-800 rounded-bl-md"
              }`}
            >
              <div className="text-sm prose prose-sm max-w-none prose-p:my-1">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-200/50">
                  <button
                    onClick={() =>
                      setExpandedSources(expandedSources === idx ? null : idx)
                    }
                    className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
                  >
                    <FileText className="w-3 h-3" />
                    {msg.sources.length} Quelle
                    {msg.sources.length > 1 ? "n" : ""}
                    {expandedSources === idx ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>
                  {expandedSources === idx && (
                    <div className="mt-2 space-y-2">
                      {msg.sources.map((src, srcIdx) => (
                        <div
                          key={srcIdx}
                          className="text-xs bg-white/50 rounded-lg p-2 border border-slate-100"
                        >
                          <div className="font-medium text-slate-700 mb-1">
                            {src.filename}
                          </div>
                          <div className="text-slate-500 line-clamp-2">
                            {src.content_snippet}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
                <span className="text-sm text-slate-500">Denke nach...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-100 p-3">
        {/* Test Cases Toggle */}
        <div className="flex items-center justify-end mb-2">
          <label className="flex items-center gap-2 text-xs text-slate-500 cursor-pointer">
            <input
              type="checkbox"
              checked={includeTestCases}
              onChange={(e) => setIncludeTestCases(e.target.checked)}
              className="w-3.5 h-3.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            Testfälle einbeziehen
          </label>
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Frage zum DDD stellen..."
            className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
