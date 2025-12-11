"use client";

import { useState, useRef, useEffect } from "react";
import AppLayout from "../components/AppLayout";

const API_URL = "http://localhost:8000";

interface Message {
    role: "user" | "assistant";
    content: string;
    sources?: Source[];
    timestamp: Date;
}

interface Source {
    filename: string;
    content: string;
    score: number;
    doc_type: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [showSources, setShowSources] = useState<number | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Send message to RAG chat API
    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            role: "user",
            content: input.trim(),
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const conversationHistory = messages.slice(-6).map(m => ({
                role: m.role,
                content: m.content
            }));

            const res = await fetch(`${API_URL}/api/documents/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: userMessage.content,
                    conversation_history: conversationHistory,
                    num_chunks: 5
                })
            });

            if (!res.ok) throw new Error("Chat request failed");

            const data = await res.json();

            setMessages(prev => [...prev, {
                role: "assistant",
                content: data.answer,
                sources: data.sources || [],
                timestamp: new Date()
            }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "❌ Fehler bei der Anfrage. Bitte prüfen Sie, ob das Backend läuft und Qdrant erreichbar ist.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const clearChat = () => {
        setMessages([]);
        setShowSources(null);
    };

    return (
        <AppLayout>
            <div className="flex flex-col h-full overflow-hidden">
                {/* Page Header */}
                <div className="flex items-center justify-between mb-4 flex-shrink-0">
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">Dokumenten-Chat</h1>
                        <p className="text-sm text-slate-500">RAG-basierte Fragen an Ihre hochgeladenen Dokumente</p>
                    </div>
                    {messages.length > 0 && (
                        <button
                            onClick={clearChat}
                            className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-red-200"
                        >
                            Chat löschen
                        </button>
                    )}
                </div>

                {/* Messages Container */}
                <div className="flex-1 overflow-auto bg-white rounded-2xl border border-slate-200 mb-4">
                    <div className="p-6 space-y-6">
                        {messages.length === 0 ? (
                            <div className="text-center py-16">
                                <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                    </svg>
                                </div>
                                <h2 className="text-xl font-bold text-slate-900 mb-2">Fragen Sie Ihre Dokumente</h2>
                                <p className="text-slate-500 mb-6 max-w-md mx-auto text-sm">
                                    Stellen Sie Fragen zu Ihren hochgeladenen Dokumenten. Die KI durchsucht die Wissensbasis und antwortet basierend auf den Inhalten.
                                </p>
                                <div className="flex flex-wrap gap-2 justify-center">
                                    {["Was ist Streamworks?", "Welche Arten von Jobs gibt es?", "Wie funktioniert ein FileTransfer?"].map((s, i) => (
                                        <button
                                            key={i}
                                            onClick={() => setInput(s)}
                                            className="px-4 py-2 bg-slate-50 border border-slate-200 rounded-full text-sm text-slate-600 hover:border-blue-300 hover:text-blue-600 transition-colors"
                                        >
                                            {s}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            messages.map((message, index) => (
                                <div key={index} className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                                    {message.role === "assistant" && (
                                        <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
                                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                            </svg>
                                        </div>
                                    )}
                                    <div className={`max-w-[75%] ${message.role === "user" ? "order-1" : ""}`}>
                                        <div className={`rounded-2xl px-4 py-3 ${message.role === "user"
                                                ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white"
                                                : "bg-slate-100 text-slate-800"
                                            }`}>
                                            <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                                        </div>

                                        {message.sources && message.sources.length > 0 && (
                                            <div className="mt-2">
                                                <button
                                                    onClick={() => setShowSources(showSources === index ? null : index)}
                                                    className="text-xs text-slate-500 hover:text-blue-600 flex items-center gap-1"
                                                >
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                                                    </svg>
                                                    {message.sources.length} Quellen {showSources === index ? "ausblenden" : "anzeigen"}
                                                </button>

                                                {showSources === index && (
                                                    <div className="mt-2 space-y-2">
                                                        {message.sources.map((source, sIndex) => (
                                                            <div key={sIndex} className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                                                                <div className="flex items-center gap-2 mb-1">
                                                                    <span className="text-xs font-medium text-blue-600 px-2 py-0.5 bg-blue-50 rounded">
                                                                        {source.doc_type.toUpperCase()}
                                                                    </span>
                                                                    <span className="text-xs font-medium text-slate-700">{source.filename}</span>
                                                                    <span className="text-xs text-slate-400 ml-auto">{(source.score * 100).toFixed(0)}%</span>
                                                                </div>
                                                                <p className="text-xs text-slate-600 line-clamp-2">{source.content}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        )}

                                        <span className="text-xs text-slate-400 mt-1 block">
                                            {message.timestamp.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}
                                        </span>
                                    </div>
                                    {message.role === "user" && (
                                        <div className="w-9 h-9 bg-slate-200 rounded-xl flex items-center justify-center flex-shrink-0">
                                            <svg className="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                            </svg>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}

                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0">
                                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                    </svg>
                                </div>
                                <div className="bg-slate-100 rounded-2xl px-4 py-3">
                                    <div className="flex gap-1.5">
                                        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></span>
                                        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></span>
                                        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Input Area */}
                <div className="flex gap-3 flex-shrink-0">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Stellen Sie eine Frage zu Ihren Dokumenten..."
                        rows={1}
                        className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-slate-800 bg-white"
                        style={{ minHeight: "48px", maxHeight: "120px" }}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!input.trim() || isLoading}
                        className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        {isLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                        ) : (
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        )}
                        Senden
                    </button>
                </div>
            </div>
        </AppLayout>
    );
}
