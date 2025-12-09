"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface AutoSaveState {
    status: "idle" | "saving" | "saved" | "error";
    lastSaved: Date | null;
}

export function useAutoSave(
    sessionId: string | null,
    data: Record<string, unknown>,
    delay: number = 3000
) {
    const [saveState, setSaveState] = useState<AutoSaveState>({
        status: "idle",
        lastSaved: null,
    });
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);
    const previousDataRef = useRef<string>("");

    const saveData = useCallback(async () => {
        if (!sessionId) return;

        setSaveState((prev) => ({ ...prev, status: "saving" }));

        try {
            const response = await fetch(
                `http://localhost:8000/api/wizard/sessions/${sessionId}/autosave`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ params: data }),
                }
            );

            if (response.ok) {
                setSaveState({
                    status: "saved",
                    lastSaved: new Date(),
                });
                // Reset to idle after 2 seconds
                setTimeout(() => {
                    setSaveState((prev) =>
                        prev.status === "saved" ? { ...prev, status: "idle" } : prev
                    );
                }, 2000);
            } else {
                setSaveState((prev) => ({ ...prev, status: "error" }));
            }
        } catch {
            setSaveState((prev) => ({ ...prev, status: "error" }));
        }
    }, [sessionId, data]);

    useEffect(() => {
        const currentData = JSON.stringify(data);

        // Only trigger save if data actually changed
        if (currentData === previousDataRef.current) return;
        previousDataRef.current = currentData;

        // Clear existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
        }

        // Set new timeout for debounced save
        timeoutRef.current = setTimeout(() => {
            saveData();
        }, delay);

        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
        };
    }, [data, delay, saveData]);

    return saveState;
}
