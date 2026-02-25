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

export interface WizardSession {
  id: string;
  data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface AnalyzeResult {
  job_type: string;
  confidence: number;
  parameters: Record<string, any>;
  suggestions: string[];
}

export interface GenerateXmlResult {
  xml: string;
  filename: string;
  warnings: string[];
}

export interface OptionItem {
  label: string;
  value: string;
}

/* ------------------------------------------------------------------ */
/* Query Keys                                                          */
/* ------------------------------------------------------------------ */

const keys = {
  sessions: ["wizard-sessions"] as const,
  session: (id: string) => ["wizard-session", id] as const,
  options: (category: string) => ["options", category] as const,
};

/* ------------------------------------------------------------------ */
/* Queries                                                             */
/* ------------------------------------------------------------------ */

export function useWizardSessions() {
  return useQuery<WizardSession[]>({
    queryKey: keys.sessions,
    queryFn: () => apiFetch<WizardSession[]>("/api/wizard/sessions"),
  });
}

export function useWizardSession(id: string | null) {
  return useQuery<WizardSession>({
    queryKey: keys.session(id ?? ""),
    queryFn: () => apiFetch<WizardSession>(`/api/wizard/sessions/${id}`),
    enabled: !!id,
  });
}

export function useOptions(category: string) {
  return useQuery<OptionItem[]>({
    queryKey: keys.options(category),
    queryFn: () => apiFetch<OptionItem[]>(`/api/options/${category}`),
    enabled: !!category,
  });
}

/* ------------------------------------------------------------------ */
/* Mutations                                                           */
/* ------------------------------------------------------------------ */

export function useCreateSession() {
  const qc = useQueryClient();

  return useMutation<WizardSession>({
    mutationFn: () =>
      apiFetch<WizardSession>("/api/wizard/sessions", { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.sessions });
    },
  });
}

export function useSaveStep(sessionId: string) {
  const qc = useQueryClient();

  return useMutation<WizardSession, Error, { step: number; data: Record<string, any> }>({
    mutationFn: (body) =>
      apiFetch<WizardSession>(`/api/wizard/sessions/${sessionId}/steps`, {
        method: "PUT",
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.session(sessionId) });
      qc.invalidateQueries({ queryKey: keys.sessions });
    },
  });
}

export function useDeleteSession() {
  const qc = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) =>
      apiFetch<void>(`/api/wizard/sessions/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: keys.sessions });
    },
  });
}

export function useAnalyze() {
  return useMutation<AnalyzeResult, Error, { description: string }>({
    mutationFn: (body) =>
      apiFetch<AnalyzeResult>("/api/wizard/analyze", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  });
}

export function useGenerateXml() {
  return useMutation<GenerateXmlResult, Error, { session_id: string }>({
    mutationFn: (body) =>
      apiFetch<GenerateXmlResult>("/api/wizard/generate-xml", {
        method: "POST",
        body: JSON.stringify(body),
      }),
  });
}
