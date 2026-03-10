"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/config";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

export interface Folder {
  id: string;
  name: string;
  color: string;
  document_count: number;
  created_at: string;
}

export interface DocumentPreview {
  id: string;
  filename: string;
  content: string;
  mime_type: string;
}

/* ------------------------------------------------------------------ */
/* Query Keys                                                          */
/* ------------------------------------------------------------------ */

export const documentKeys = {
  folders: ["doc-folders"] as const,
  preview: (id: string) => ["doc-preview", id] as const,
};

/* ------------------------------------------------------------------ */
/* Folder Hooks                                                        */
/* ------------------------------------------------------------------ */

const MOCK_FOLDERS: Folder[] = [
  { id: "mock-1", name: "Anforderungen", color: "#0066cc", document_count: 5, created_at: "2026-01-15T10:00:00Z" },
  { id: "mock-2", name: "SAP-Dokumentation", color: "#d97706", document_count: 3, created_at: "2026-01-20T08:30:00Z" },
  { id: "mock-3", name: "Betriebshandbuecher", color: "#059669", document_count: 8, created_at: "2026-02-01T14:00:00Z" },
  { id: "mock-4", name: "Vorlagen", color: "#7c3aed", document_count: 2, created_at: "2026-02-10T09:00:00Z" },
  { id: "mock-5", name: "Archiv", color: "#dc2626", document_count: 12, created_at: "2026-02-15T16:00:00Z" },
];

export function useFolders() {
  return useQuery<Folder[]>({
    queryKey: documentKeys.folders,
    queryFn: async () => {
      try {
        return await apiFetch<Folder[]>("/api/documents/folders");
      } catch {
        return MOCK_FOLDERS;
      }
    },
    placeholderData: MOCK_FOLDERS,
  });
}

export function useCreateFolder() {
  const queryClient = useQueryClient();

  return useMutation<Folder, Error, { name: string; color: string }>({
    mutationFn: (data) =>
      apiFetch<Folder>("/api/documents/folders", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.folders });
    },
  });
}

export function useUpdateFolder() {
  const queryClient = useQueryClient();

  return useMutation<
    Folder,
    Error,
    { id: string; name?: string; color?: string }
  >({
    mutationFn: ({ id, ...data }) =>
      apiFetch<Folder>(`/api/documents/folders/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.folders });
    },
  });
}

export function useDeleteFolder() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (folderId) =>
      apiFetch<void>(`/api/documents/folders/${folderId}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.folders });
      // Documents may have moved to root
      queryClient.invalidateQueries({ queryKey: ["rag-documents"] });
    },
  });
}

/* ------------------------------------------------------------------ */
/* Document Move & Preview Hooks                                       */
/* ------------------------------------------------------------------ */

export function useMoveDocument() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, { documentId: string; folderId: string | null }>({
    mutationFn: ({ documentId, folderId }) =>
      apiFetch<void>(`/api/documents/${documentId}/move`, {
        method: "PUT",
        body: JSON.stringify({ folder_id: folderId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["rag-documents"] });
      queryClient.invalidateQueries({ queryKey: documentKeys.folders });
    },
  });
}

export function useDocumentPreview(documentId: string | null) {
  return useQuery<DocumentPreview>({
    queryKey: documentKeys.preview(documentId ?? ""),
    queryFn: () =>
      apiFetch<DocumentPreview>(`/api/documents/${documentId}/preview`),
    enabled: !!documentId,
  });
}
