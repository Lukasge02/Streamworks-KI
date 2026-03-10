"use client";

import React from "react";
import {
  FileText,
  FileSpreadsheet,
  File,
  Eye,
  FolderInput,
  Trash2,
  Loader2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Document } from "@/lib/api/chat";
import type { Folder } from "@/lib/api/documents";

interface DocumentCardProps {
  doc: Document & { folder_id?: string | null };
  folders: Folder[];
  onPreview: () => void;
  onMove: () => void;
  onDelete: () => void;
  isDeleting: boolean;
}

function getFileIcon(mime: string) {
  if (mime.includes("pdf")) return FileText;
  if (mime.includes("spreadsheet") || mime.includes("csv"))
    return FileSpreadsheet;
  return File;
}

function mimeLabel(mime: string): string {
  if (mime.includes("pdf")) return "PDF";
  if (mime.includes("wordprocessingml")) return "DOCX";
  if (mime.includes("spreadsheetml")) return "XLSX";
  if (mime.includes("text/plain")) return "TXT";
  if (mime.includes("text/csv")) return "CSV";
  return mime.split("/").pop()?.toUpperCase() ?? "";
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function DocumentCard({
  doc,
  folders,
  onPreview,
  onMove,
  onDelete,
  isDeleting,
}: DocumentCardProps) {
  const Icon = getFileIcon(doc.mime_type);
  const folder = folders.find((f) => f.id === doc.folder_id);

  return (
    <div
      className={cn(
        "group relative rounded-lg border border-border bg-surface-raised p-4 transition-all duration-200",
        "hover:shadow-card hover:-translate-y-0.5"
      )}
    >
      {/* File icon + name */}
      <div className="flex flex-col items-center text-center gap-2">
        <div className="shrink-0 rounded-xl bg-accent/10 p-3">
          <Icon className="h-7 w-7 text-accent" />
        </div>
        <div className="w-full">
          <p className="font-medium text-primary text-sm leading-tight line-clamp-2">
            {doc.filename}
          </p>
          <div className="mt-1.5 flex flex-wrap items-center justify-center gap-1.5">
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
              {mimeLabel(doc.mime_type)}
            </Badge>
            <span className="text-xs text-muted-foreground">
              {formatFileSize(doc.file_size)}
            </span>
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
              {doc.chunks} Chunks
            </Badge>
          </div>
        </div>
      </div>

      {/* Folder badge + date */}
      <div className="mt-3 flex flex-col items-center gap-1">
        {folder ? (
          <div className="flex items-center gap-1.5">
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: folder.color }}
            />
            <span className="text-xs text-muted-foreground truncate max-w-[120px]">
              {folder.name}
            </span>
          </div>
        ) : (
          <span className="text-xs text-muted-foreground">Stammverzeichnis</span>
        )}
        <span className="text-xs text-muted-foreground">
          {doc.created_at ? formatDate(doc.created_at) : ""}
        </span>
      </div>

      {/* Hover actions */}
      <div className="absolute top-2 right-2 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          onClick={onPreview}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-primary transition-colors"
          title="Vorschau"
        >
          <Eye className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={onMove}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-primary transition-colors"
          title="Verschieben"
        >
          <FolderInput className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={onDelete}
          disabled={isDeleting}
          className="rounded-md p-1.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors disabled:opacity-30"
          title="Loeschen"
        >
          {isDeleting ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Trash2 className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
    </div>
  );
}
