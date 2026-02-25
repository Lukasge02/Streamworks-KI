"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import type { Source } from "@/lib/api/chat";
import { BACKEND_URL } from "@/lib/api/config";

interface StreamingChatState {
  isStreaming: boolean;
  streamedText: string;
  sources: Source[];
  confidence: number | null;
  sessionId: string | null;
}

const INITIAL_STATE: StreamingChatState = {
  isStreaming: false,
  streamedText: "",
  sources: [],
  confidence: null,
  sessionId: null,
};

/**
 * Parse a raw SSE text buffer into discrete events.
 * Each SSE event has the form:
 *   event: <type>\n
 *   data: <json>\n\n
 */
function parseSSEEvents(raw: string): Array<{ event: string; data: string }> {
  const events: Array<{ event: string; data: string }> = [];
  const blocks = raw.split("\n\n");

  for (const block of blocks) {
    if (!block.trim()) continue;

    let event = "message";
    let data = "";

    for (const line of block.split("\n")) {
      if (line.startsWith("event: ")) {
        event = line.slice(7).trim();
      } else if (line.startsWith("data: ")) {
        data = line.slice(6);
      } else if (line.startsWith("data:")) {
        data = line.slice(5);
      }
    }

    if (data) {
      events.push({ event, data });
    }
  }

  return events;
}

export function useStreamingChat() {
  const [state, setState] = useState<StreamingChatState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);

  // Abort in-flight stream on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
        abortRef.current = null;
      }
    };
  }, []);

  const reset = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    setState(INITIAL_STATE);
  }, []);

  const sendMessage = useCallback(
    async (
      message: string,
      sessionId?: string | null
    ): Promise<{ sessionId: string | null }> => {
      // Abort any in-flight stream
      if (abortRef.current) {
        abortRef.current.abort();
      }

      const controller = new AbortController();
      abortRef.current = controller;

      setState({
        isStreaming: true,
        streamedText: "",
        sources: [],
        confidence: null,
        sessionId: sessionId ?? null,
      });

      let resultSessionId: string | null = sessionId ?? null;

      try {
        const body: Record<string, unknown> = { message };
        if (sessionId) {
          body.session_id = sessionId;
        }

        const response = await fetch(`${BACKEND_URL}/api/rag/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({}));
          throw new Error(
            errBody.detail || `Streaming fehlgeschlagen: ${response.status}`
          );
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("ReadableStream nicht verfuegbar");

        const decoder = new TextDecoder();
        let buffer = "";
        let accumulatedText = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          // Try to parse complete SSE events from the buffer.
          // We look for double-newline boundaries to identify complete events.
          const lastDoubleNewline = buffer.lastIndexOf("\n\n");
          if (lastDoubleNewline === -1) continue;

          const completePart = buffer.slice(0, lastDoubleNewline + 2);
          buffer = buffer.slice(lastDoubleNewline + 2);

          const events = parseSSEEvents(completePart);

          for (const evt of events) {
            try {
              const parsed = JSON.parse(evt.data);

              switch (evt.event) {
                case "sources": {
                  const sources = (parsed.sources ?? []) as Source[];
                  resultSessionId = parsed.session_id ?? resultSessionId;
                  setState((prev) => ({
                    ...prev,
                    sources,
                    sessionId: resultSessionId,
                  }));
                  break;
                }

                case "chunk": {
                  const text = parsed.text ?? parsed.chunk ?? "";
                  accumulatedText += text;
                  setState((prev) => ({
                    ...prev,
                    streamedText: accumulatedText,
                  }));
                  break;
                }

                case "done": {
                  const confidence =
                    parsed.confidence ?? parsed.score ?? null;
                  setState((prev) => ({
                    ...prev,
                    confidence,
                    isStreaming: false,
                  }));
                  break;
                }

                case "error": {
                  throw new Error(
                    parsed.message ?? "Unbekannter Streaming-Fehler"
                  );
                }

                default:
                  break;
              }
            } catch (parseErr) {
              // If JSON parsing fails for a chunk, skip it
              if (
                parseErr instanceof Error &&
                parseErr.message !== "Unbekannter Streaming-Fehler"
              ) {
                // Non-JSON data, might be a plain text chunk
              } else {
                throw parseErr;
              }
            }
          }
        }

        // Make sure streaming is marked as done even if no "done" event arrived
        setState((prev) => ({
          ...prev,
          isStreaming: false,
        }));
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") {
          // Intentional abort - do nothing
        } else {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            streamedText:
              prev.streamedText ||
              `Fehler: ${err instanceof Error ? err.message : "Unbekannter Fehler"}`,
          }));
        }
      }

      return { sessionId: resultSessionId };
    },
    []
  );

  return {
    sendMessage,
    isStreaming: state.isStreaming,
    streamedText: state.streamedText,
    sources: state.sources,
    confidence: state.confidence,
    sessionId: state.sessionId,
    reset,
  };
}
