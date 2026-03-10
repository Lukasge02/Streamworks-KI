"use client";

import React from "react";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDocumentPreview } from "@/lib/api/documents";

interface DocumentPreviewDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentId: string | null;
}

function mimeLabel(mime: string): string {
  if (mime.includes("pdf")) return "PDF";
  if (mime.includes("wordprocessingml")) return "DOCX";
  if (mime.includes("spreadsheetml")) return "XLSX";
  if (mime.includes("text/plain")) return "TXT";
  if (mime.includes("text/csv")) return "CSV";
  return mime.split("/").pop()?.toUpperCase() ?? "Datei";
}

export default function DocumentPreviewDialog({
  open,
  onOpenChange,
  documentId,
}: DocumentPreviewDialogProps) {
  const { data: preview, isLoading } = useDocumentPreview(
    open ? documentId : null
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <DialogTitle className="truncate">
              {preview?.filename ?? "Vorschau"}
            </DialogTitle>
            {preview?.mime_type && (
              <Badge variant="secondary" className="text-[10px] shrink-0">
                {mimeLabel(preview.mime_type)}
              </Badge>
            )}
          </div>
        </DialogHeader>

        <div className="flex-1 min-h-0 overflow-y-auto rounded-md border border-border bg-muted/30 p-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-2">
              <Loader2 className="h-6 w-6 animate-spin text-accent" />
              <p className="text-sm text-muted-foreground">
                Vorschau wird geladen...
              </p>
            </div>
          ) : preview?.content ? (
            <pre className="whitespace-pre-wrap text-sm text-primary font-mono leading-relaxed">
              {preview.content}
            </pre>
          ) : (
            <p className="text-sm text-muted-foreground text-center py-8">
              Keine Vorschau verfuegbar.
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
