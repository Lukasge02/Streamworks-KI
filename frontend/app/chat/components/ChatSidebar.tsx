"use client";

import React, { useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquarePlus,
  Trash2,
  FileText,
  Upload,
  Loader2,
  File,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import {
  useChatSessions,
  useDeleteChatSession,
  useDocuments,
  useUploadDocument,
  useDeleteDocument,
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

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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
/* Document Item                                                       */
/* ------------------------------------------------------------------ */

function DocumentItem({
  doc,
  onDelete,
  isDeleting,
}: {
  doc: { id: string; filename: string; file_size: number; chunks: number };
  onDelete: () => void;
  isDeleting: boolean;
}) {
  return (
    <div className="group flex items-start gap-2 rounded-md px-3 py-2 text-sm hover:bg-muted transition-colors">
      <File className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-primary leading-tight">
          {doc.filename}
        </p>
        <div className="mt-1 flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            {formatFileSize(doc.file_size)}
          </span>
          <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
            {doc.chunks} Chunks
          </Badge>
        </div>
      </div>
      <button
        onClick={onDelete}
        disabled={isDeleting}
        className="shrink-0 rounded-sm p-1 opacity-0 transition-opacity group-hover:opacity-70 hover:!opacity-100 hover:text-destructive disabled:opacity-30"
        title="Dokument loeschen"
      >
        {isDeleting ? (
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
        ) : (
          <X className="h-3.5 w-3.5" />
        )}
      </button>
    </div>
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
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Data
  const { data: sessions = [], isLoading: sessionsLoading } =
    useChatSessions();
  const { data: documents = [], isLoading: docsLoading } = useDocuments();

  // Mutations
  const deleteSession = useDeleteChatSession();
  const uploadDoc = useUploadDocument();
  const deleteDoc = useDeleteDocument();

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

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    uploadDoc.mutate(file, {
      onSuccess: (data) => {
        toast.success(`"${data.filename}" hochgeladen (${data.chunks} Chunks)`);
      },
      onError: (err) => toast.error(err.message),
    });

    // Reset the input so the same file can be re-selected
    e.target.value = "";
  }

  function handleDeleteDocument(id: string) {
    deleteDoc.mutate(id, {
      onSuccess: () => toast.success("Dokument geloescht"),
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

      {/* ---- Separator ---- */}
      <div className="mx-4 border-t border-border" />

      {/* ---- Documents ---- */}
      <div className="flex flex-col gap-1 p-2">
        <div className="flex items-center justify-between px-3 py-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Dokumente
          </p>
          <span className="text-xs text-muted-foreground">
            {documents.length}
          </span>
        </div>

        {/* Upload button */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.xlsx,.txt"
          onChange={handleFileChange}
          className="hidden"
        />
        <Button
          variant="outline"
          size="sm"
          className="mx-2 gap-2"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadDoc.isPending}
        >
          {uploadDoc.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Upload className="h-3.5 w-3.5" />
          )}
          {uploadDoc.isPending ? "Wird hochgeladen..." : "Dokument hochladen"}
        </Button>

        {/* Document list */}
        <div className="mt-1 max-h-48 overflow-y-auto scrollbar-thin">
          {docsLoading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}

          {!docsLoading && documents.length === 0 && (
            <div className="flex flex-col items-center gap-1 px-3 py-4 text-center">
              <FileText className="h-5 w-5 text-muted-foreground/50" />
              <p className="text-xs text-muted-foreground">
                Keine Dokumente vorhanden
              </p>
            </div>
          )}

          {documents.map((doc) => (
            <DocumentItem
              key={doc.id}
              doc={doc}
              onDelete={() => handleDeleteDocument(doc.id)}
              isDeleting={
                deleteDoc.isPending && deleteDoc.variables === doc.id
              }
            />
          ))}
        </div>
      </div>

      {/* Bottom padding */}
      <div className="h-2" />
    </aside>
  );
}
