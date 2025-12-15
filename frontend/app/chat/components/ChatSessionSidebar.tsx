"use client";

import { useState, useImperativeHandle, forwardRef } from "react";
import {
  useChatSessions,
  useDeleteChatSession,
  useDeleteAllChatSessions,
} from "../../../lib/api/chat";
import { apiMutate } from "../../../lib/api/config";
import { useQueryClient } from "@tanstack/react-query";

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatSessionSidebarProps {
  activeSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewChat: () => void;
}

export interface ChatSessionSidebarRef {
  refreshSessions: () => Promise<void>;
}

const ChatSessionSidebar = forwardRef<
  ChatSessionSidebarRef,
  ChatSessionSidebarProps
>(({ activeSessionId, onSessionSelect, onNewChat }, ref) => {
  const queryClient = useQueryClient();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  // TanStack Query hooks
  const { data, isLoading, refetch } = useChatSessions();
  const deleteMutation = useDeleteChatSession();
  const deleteAllMutation = useDeleteAllChatSessions();

  const sessions: ChatSession[] = (data as any)?.sessions || [];

  // Expose refresh method to parent
  useImperativeHandle(ref, () => ({
    refreshSessions: async () => {
      await refetch();
    },
  }));

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    setSessionToDelete(sessionId);
  };

  const confirmDeleteSession = () => {
    if (!sessionToDelete) return;

    deleteMutation.mutate(sessionToDelete, {
      onSuccess: () => {
        if (activeSessionId === sessionToDelete) {
          onNewChat();
        }
        setSessionToDelete(null);
      },
    });
  };

  const handleRename = async (sessionId: string) => {
    if (!editTitle.trim()) {
      setEditingId(null);
      return;
    }

    try {
      await apiMutate<{ success: boolean }>(
        `/api/documents/chat/sessions/${sessionId}`,
        "PATCH",
        { title: editTitle }
      );
      await refetch();
    } catch (error) {
      console.error("Failed to rename session:", error);
    } finally {
      setEditingId(null);
    }
  };

  const confirmDeleteAll = () => {
    deleteAllMutation.mutate(undefined, {
      onSuccess: () => {
        onNewChat();
        setShowDeleteConfirm(false);
      },
    });
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "Heute";
    if (days === 1) return "Gestern";
    if (days < 7) return `Vor ${days} Tagen`;
    return date.toLocaleDateString("de-DE", { day: "2-digit", month: "short" });
  };

  return (
    <div className="w-72 bg-gradient-to-b from-slate-50 to-slate-100 border-r border-slate-200 flex flex-col h-full shadow-sm">
      {/* Header with New Chat button */}
      <div className="p-4 border-b border-slate-200/80">
        <button
          onClick={onNewChat}
          className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg shadow-blue-500/30 flex items-center justify-center gap-2 group"
        >
          <svg
            className="w-5 h-5 transition-transform group-hover:rotate-90"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Neuer Chat
        </button>
      </div>

      {/* Section Title & Delete All */}
      <div className="px-4 pt-4 pb-2 flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Chat-Verlauf
        </h3>
        {sessions.length > 0 && (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={deleteAllMutation.isPending}
            className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
            title="Alle Chats löschen"
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
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        )}
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-12 px-4">
            <div className="w-12 h-12 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-3">
              <svg
                className="w-6 h-6 text-slate-400"
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
            <p className="text-sm text-slate-500">Noch keine Chats</p>
            <p className="text-xs text-slate-400 mt-1">
              Starten Sie eine neue Konversation
            </p>
          </div>
        ) : (
          <div className="space-y-1 pb-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => onSessionSelect(session.id)}
                className={`group relative px-3 py-3 rounded-xl cursor-pointer transition-all ${activeSessionId === session.id
                  ? "bg-white border border-blue-200 shadow-sm"
                  : "hover:bg-white/60 border border-transparent"
                  }`}
              >
                {editingId === session.id ? (
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    onBlur={() => handleRename(session.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleRename(session.id);
                      if (e.key === "Escape") setEditingId(null);
                    }}
                    autoFocus
                    className="w-full px-2 py-1 text-sm border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <div className="flex items-start gap-3">
                    {/* Chat Icon */}
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${activeSessionId === session.id
                        ? "bg-blue-100 text-blue-600"
                        : "bg-slate-100 text-slate-400 group-hover:bg-slate-200"
                        }`}
                    >
                      <svg
                        className="w-4 h-4"
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

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p
                        className={`text-sm font-medium truncate ${activeSessionId === session.id
                          ? "text-blue-900"
                          : "text-slate-700"
                          }`}
                      >
                        {session.title}
                      </p>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className="text-xs text-slate-400">
                          {formatDate(session.updated_at)}
                        </span>
                        {session.message_count > 0 && (
                          <>
                            <span className="text-slate-300">•</span>
                            <span className="text-xs text-slate-400">
                              {session.message_count}{" "}
                              {session.message_count === 1
                                ? "Nachricht"
                                : "Nachrichten"}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditTitle(session.title);
                          setEditingId(session.id);
                        }}
                        className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Umbenennen"
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
                            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => handleDelete(e, session.id)}
                        disabled={deleteMutation.isPending}
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        title="Löschen"
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
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-200/80 bg-slate-50/50">
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="w-full py-2 text-xs text-slate-500 hover:text-blue-600 hover:bg-white flex items-center justify-center gap-1.5 rounded-lg transition-colors disabled:opacity-50"
        >
          <svg
            className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Aktualisieren
        </button>
      </div>
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/20 backdrop-blur-sm p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 p-4 w-full max-w-[240px] animate-in fade-in zoom-in duration-200">
            <h4 className="text-sm font-semibold text-slate-800 mb-2">Alle löschen?</h4>
            <p className="text-xs text-slate-500 mb-4">
              Dies kann nicht rückgängig gemacht werden.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 px-3 py-2 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={confirmDeleteAll}
                disabled={deleteAllMutation.isPending}
                className="flex-1 px-3 py-2 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Löschen
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Single Delete Confirmation Modal */}
      {sessionToDelete && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/20 backdrop-blur-sm p-4">
          <div className="bg-white rounded-xl shadow-xl border border-slate-200 p-4 w-full max-w-[240px] animate-in fade-in zoom-in duration-200">
            <h4 className="text-sm font-semibold text-slate-800 mb-2">Chat löschen?</h4>
            <div className="flex gap-2">
              <button
                onClick={() => setSessionToDelete(null)}
                className="flex-1 px-3 py-2 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Abbrechen
              </button>
              <button
                onClick={confirmDeleteSession}
                disabled={deleteMutation.isPending}
                className="flex-1 px-3 py-2 text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Löschen
              </button>
            </div>
          </div>
        </div>
      )}
    </div >
  );
});

ChatSessionSidebar.displayName = "ChatSessionSidebar";

export default ChatSessionSidebar;
