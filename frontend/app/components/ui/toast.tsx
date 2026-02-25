"use client";

import * as React from "react";
import { create } from "zustand";
import { cn } from "@/lib/utils";
import { X, CheckCircle2, AlertCircle, Info } from "lucide-react";

/* ------------------------------------------------------------------ */
/* Toast Store                                                        */
/* ------------------------------------------------------------------ */

type ToastVariant = "success" | "error" | "info";

interface Toast {
  id: string;
  message: string;
  variant: ToastVariant;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (message: string, variant: ToastVariant) => void;
  removeToast: (id: string) => void;
}

const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (message, variant) => {
    const id = crypto.randomUUID();
    set((state) => ({
      toasts: [...state.toasts, { id, message, variant }],
    }));
    setTimeout(() => {
      set((state) => ({
        toasts: state.toasts.filter((t) => t.id !== id),
      }));
    }, 4000);
  },
  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));

/* ------------------------------------------------------------------ */
/* useToast Hook                                                      */
/* ------------------------------------------------------------------ */

export function useToast() {
  const addToast = useToastStore((s) => s.addToast);

  return {
    success: (message: string) => addToast(message, "success"),
    error: (message: string) => addToast(message, "error"),
    info: (message: string) => addToast(message, "info"),
  };
}

/* ------------------------------------------------------------------ */
/* Variant Config                                                     */
/* ------------------------------------------------------------------ */

const variantConfig: Record<
  ToastVariant,
  { icon: React.ElementType; containerClass: string }
> = {
  success: {
    icon: CheckCircle2,
    containerClass: "border-success/30 bg-success-light text-success",
  },
  error: {
    icon: AlertCircle,
    containerClass:
      "border-destructive/30 bg-destructive-light text-destructive",
  },
  info: {
    icon: Info,
    containerClass: "border-accent/30 bg-blue-50 text-accent",
  },
};

/* ------------------------------------------------------------------ */
/* Toaster Component                                                  */
/* ------------------------------------------------------------------ */

export function Toaster() {
  const toasts = useToastStore((s) => s.toasts);
  const removeToast = useToastStore((s) => s.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((toast) => {
        const config = variantConfig[toast.variant];
        const Icon = config.icon;

        return (
          <div
            key={toast.id}
            className={cn(
              "flex items-center gap-3 rounded-lg border px-4 py-3 shadow-elevated animate-slide-in-right",
              "min-w-[320px] max-w-[420px]",
              config.containerClass
            )}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="flex-1 text-sm font-medium">
              {toast.message}
            </span>
            <button
              onClick={() => removeToast(toast.id)}
              className="shrink-0 rounded-sm opacity-70 hover:opacity-100 transition-opacity"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
