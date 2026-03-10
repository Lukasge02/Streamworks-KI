"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { apiFetch, BACKEND_URL } from "@/lib/api/config";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

export interface Source {
  document_name: string;
  chunk_text: string;
  score: number;
  page?: number;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  session_id: string;
  confidence: number;
}

export interface Document {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  chunks: number;
  created_at: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  chunks: number;
  message: string;
}

/* ------------------------------------------------------------------ */
/* Query Keys                                                          */
/* ------------------------------------------------------------------ */

export const chatKeys = {
  sessions: ["chat-sessions"] as const,
  messages: (sessionId: string) => ["chat-messages", sessionId] as const,
  documents: ["rag-documents"] as const,
};

/* ------------------------------------------------------------------ */
/* Session Hooks                                                       */
/* ------------------------------------------------------------------ */

export function useChatSessions() {
  return useQuery<ChatSession[]>({
    queryKey: chatKeys.sessions,
    queryFn: () => apiFetch<ChatSession[]>("/api/rag/sessions"),
  });
}

export function useChatMessages(sessionId: string | null) {
  return useQuery<ChatMessage[]>({
    queryKey: chatKeys.messages(sessionId ?? ""),
    queryFn: () =>
      apiFetch<ChatMessage[]>(`/api/rag/sessions/${sessionId}/messages`),
    enabled: !!sessionId,
  });
}

export function useDeleteChatSession() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (sessionId) =>
      apiFetch<void>(`/api/rag/sessions/${sessionId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.sessions });
    },
  });
}

/* ------------------------------------------------------------------ */
/* Document Hooks                                                      */
/* ------------------------------------------------------------------ */

export function useDocuments() {
  return useQuery<Document[]>({
    queryKey: chatKeys.documents,
    queryFn: () => apiFetch<Document[]>("/api/documents/"),
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation<UploadResponse, Error, { file: File; folderId?: string | null }>({
    mutationFn: async ({ file, folderId }) => {
      const formData = new FormData();
      formData.append("file", file);

      let url = `${BACKEND_URL}/api/documents/upload`;
      if (folderId) {
        url += `?folder_id=${encodeURIComponent(folderId)}`;
      }

      const res = await fetch(url, {
        method: "POST",
        body: formData,
        // Do NOT set Content-Type header -- browser sets multipart boundary
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(
          body.detail || `Upload fehlgeschlagen: ${res.status}`
        );
      }

      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.documents });
      queryClient.invalidateQueries({ queryKey: ["doc-folders"] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (documentId) =>
      apiFetch<void>(`/api/documents/${documentId}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: chatKeys.documents });
    },
  });
}
