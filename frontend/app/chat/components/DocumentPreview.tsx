"use client";

import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { FileText, Hash, TrendingUp } from "lucide-react";
import type { Source } from "@/lib/api/chat";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface DocumentPreviewProps {
  source: Source | null;
  open: boolean;
  onClose: () => void;
}

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function scoreToPercent(score: number): number {
  return Math.round(score * 100);
}

function scoreVariant(score: number) {
  if (score >= 0.8) return "success" as const;
  if (score >= 0.5) return "warning" as const;
  return "destructive" as const;
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function DocumentPreview({
  source,
  open,
  onClose,
}: DocumentPreviewProps) {
  if (!source) return null;

  const percent = scoreToPercent(source.score);

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-accent" />
            Quellenvorschau
          </DialogTitle>
          <DialogDescription>
            Details zur referenzierten Textstelle
          </DialogDescription>
        </DialogHeader>

        {/* Meta badges */}
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary" className="gap-1.5">
            <FileText className="h-3 w-3" />
            {source.document_name}
          </Badge>

          {source.page != null && (
            <Badge variant="outline" className="gap-1.5">
              <Hash className="h-3 w-3" />
              Seite {source.page}
            </Badge>
          )}

          <Badge variant={scoreVariant(source.score)} className="gap-1.5">
            <TrendingUp className="h-3 w-3" />
            {percent}% Relevanz
          </Badge>
        </div>

        {/* Chunk text */}
        <div className="mt-2 max-h-[50vh] overflow-y-auto rounded-md border border-border bg-surface-sunken p-4 scrollbar-thin">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-primary">
            {source.chunk_text}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
