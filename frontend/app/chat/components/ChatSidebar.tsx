"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquarePlus,
  Trash2,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import {
  useChatSessions,
  useDeleteChatSession,
  type ChatSession,
} from "@/lib/api/chat";
import { cn } from "@/lib/utils";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface ChatSidebarProps {
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Heute";
  if (diffDays === 1) return "Gestern";
  if (diffDays < 7) return `Vor ${diffDays} Tagen`;

  return date.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

/* ------------------------------------------------------------------ */
/* Session Item                                                        */
/* ------------------------------------------------------------------ */

function SessionItem({
  session,
  isActive,
  onSelect,
  onDelete,
}: {
  session: ChatSession;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -8 }}
      className={cn(
        "group flex items-center gap-2 rounded-md px-3 py-2.5 text-sm cursor-pointer transition-colors",
        isActive
          ? "bg-accent/10 text-accent border border-accent/20"
          : "text-muted-foreground hover:bg-muted hover:text-primary"
      )}
      onClick={onSelect}
    >
      <MessageSquarePlus className="h-4 w-4 shrink-0 opacity-60" />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium leading-tight">
          {session.title || "Neue Unterhaltung"}
        </p>
        <p className="mt-0.5 text-xs opacity-60">
          {formatDate(session.updated_at || session.created_at)}
        </p>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="shrink-0 rounded-sm p-1 opacity-0 transition-opacity group-hover:opacity-70 hover:!opacity-100 hover:text-destructive"
        title="Sitzung loeschen"
      >
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Sidebar                                                        */
/* ------------------------------------------------------------------ */

export default function ChatSidebar({
  activeSessionId,
  onSelectSession,
  onNewChat,
}: ChatSidebarProps) {
  const toast = useToast();

  // Data
  const { data: sessions = [], isLoading: sessionsLoading } =
    useChatSessions();

  // Mutations
  const deleteSession = useDeleteChatSession();

  // Handlers
  function handleDeleteSession(id: string) {
    deleteSession.mutate(id, {
      onSuccess: () => {
        toast.success("Sitzung geloescht");
        if (activeSessionId === id) {
          onNewChat();
        }
      },
      onError: (err) => toast.error(err.message),
    });
  }

  // Sort sessions: most recent first
  const sortedSessions = [...sessions].sort(
    (a, b) =>
      new Date(b.updated_at || b.created_at).getTime() -
      new Date(a.updated_at || a.created_at).getTime()
  );

  return (
    <aside className="flex h-full w-72 flex-col border-r border-border bg-surface-raised">
      {/* ---- Header ---- */}
      <div className="flex items-center gap-2 border-b border-border p-4">
        <Button
          onClick={onNewChat}
          className="w-full gap-2"
          variant="default"
          size="default"
        >
          <MessageSquarePlus className="h-4 w-4" />
          Neuer Chat
        </Button>
      </div>

      {/* ---- Sessions ---- */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-2">
        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Unterhaltungen
        </p>

        {sessionsLoading && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        )}

        {!sessionsLoading && sortedSessions.length === 0 && (
          <p className="px-3 py-4 text-xs text-muted-foreground">
            Noch keine Unterhaltungen vorhanden.
          </p>
        )}

        <AnimatePresence initial={false}>
          <div className="flex flex-col gap-0.5">
            {sortedSessions.map((session) => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={session.id === activeSessionId}
                onSelect={() => onSelectSession(session.id)}
                onDelete={() => handleDeleteSession(session.id)}
              />
            ))}
          </div>
        </AnimatePresence>
      </div>
    </aside>
  );
}
